# Retrievers

## 1. MultiQueryRetriever

La búsqueda semántica tradicional se basa en calcular la distancia vectorial entre la consulta del usuario y los fragmentos (_chunks_) de texto. Si el usuario formula una pregunta vaga, con errores ortográficos, o utilizando una terminología distinta a la del documento fuente, el sistema puede pasar por alto información crucial.

MultiQueryRetriever automatiza el proceso de ingeniería de prompts utilizando un Modelo de Lenguaje (LLM) para generar múltiples variantes de la consulta original desde diferentes perspectivas. Luego ejecuta todas las consultas en paralelo y unifica los resultados.

**Cuándo usarlo**:

- Interfaces de chat públicas donde los usuarios finales escriben de forma coloquial, poco clara o imprecisa.
- Cuando tu consulta original puede ser interpretada de múltiples formas.
- Cuando la exhaustividad es más importante que la velocidad (ej. auditorías legales o investigación médica).
- Para mejorar la diversidad de resultados recuperados.
- En casos donde la consulta inicial podría no capturar todos los aspectos relevantes.

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

# Configurar el retriever
llm = ChatOpenAI(temperature=0)
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=vector_store.as_retriever(),
    llm=llm,
    verbose=True  # Ver las consultas generadas
)

# Una pregunta se convierte en múltiples perspectivas
results = multi_query_retriever.invoke("¿Cómo aprenden las redes neuronales?")
```

## 2. ContextualCompressionRetriever

Cuando un recuperador tradicional extrae documentos, suele devolver fragmentos enteros de texto que contienen tanto información valiosa como contenido irrelevante (_ruido_). Pasar fragmentos grandes al LLM consume ventanas de contexto innecesarias, incrementa los costos de API y puede confundir al modelo (fenómeno de "pérdida en el medio").

ContextualCompressionRetriever resuelve esto comprimiendo los documentos devueltos en función del contexto de la consulta. Utiliza un filtro de paso (que puede ser otro LLM más pequeño o un algoritmo) para extraer únicamente las oraciones o párrafos que responden directamente a la pregunta, descartando el relleno.

**Cuándo usarlo**:

- Cuando tus documentos fuente son densos, extensos y conversacionales (ej. transcripciones de llamadas, contratos de cientos de páginas, minutas de reuniones).
- Optimización de costos en sistemas con alto volumen de tráfico.

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Crear compresor que extrae solo contenido relevante
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_store.as_retriever()
)

# Solo obtener las partes relevantes
compressed_results = compression_retriever.invoke(
    "Explica el algoritmo de retropropagación"
)


Pipeline avanzado de compresión

from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_text_splitters import CharacterTextSplitter

# Pipeline: dividir -> filtrar redundantes -> comprimir por relevancia
splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0, separator=".")
redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
relevant_filter = LLMChainExtractor.from_llm(llm)

pipeline_compressor = DocumentCompressorPipeline(
    transformers=[splitter, redundant_filter, relevant_filter]
)
```

## 3. EnsembleRetriever

La búsqueda semántica (basada en _embeddings_) es excelente para capturar conceptos generales y sinónimos, pero suele fallar cuando el usuario busca palabras clave sumamente específicas, números de serie, códigos de error o nombres de productos exactos. Por otro lado, la búsqueda tradicional por palabras clave (como BM25) es excelente con los términos exactos, pero no entiende el contexto ni la intención subyacente.

EnsembleRetriever resuelve este dilema combinando los resultados de múltiples retrievers (normalmente un recuperador semántico vectorial y uno léxico como BM25). Utiliza algoritmos de ordenación cruzada como el Rank Fusion RRF (Reciprocal Rank Fusion) para promediar y reordenar los mejores resultados de ambos mundos.

**Cuándo usarlo**:

- Búsquedas que requieren tanto precisión léxica como semántica, por ejemplo, motores de búsqueda de comercio electrónico (donde los usuarios buscan tanto conceptos "ropa cómoda para invierno" como códigos "SKU-9942").
- Sistemas de búsqueda empresarial.
- Soporte técnico de TI o documentación de software, donde conviven explicaciones conceptuales y códigos de error alfanuméricos.

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Crear retriever BM25 (búsqueda por palabras clave)
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

# Crear retriever vectorial (búsqueda semántica)
embedding = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embedding)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Combinar ambos con pesos
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7]  # 30% BM25, 70% vectorial
)
```

## 4. ParentDocumentRetriever

Al procesar documentos para un sistema RAG, existe un conflicto de diseño:

1. Si divides el documento en fragmentos **pequeños**, sus embeddings representarán con gran precisión el significado semántico de ese fragmento específico. Sin embargo, al recuperarlo, puede faltar contexto esencial.
2. Si los fragmentos son **grandes**, conservan el contexto, pero sus embeddings se diluyen y vuelven imprecisos, perjudicando la búsqueda.

ParentDocumentRetriever resuelve esto separando el texto guardado para la búsqueda del texto enviado al LLM. Divide los documentos en pequeños fragmentos hijo (para optimizar la búsqueda semántica). Pero cuando un fragmento hijo es seleccionado, el recuperador busca en una base de datos secundaria el documento "Padre" completo (o un fragmento considerablemente mayor) y se lo entrega al LLM.

**Cuándo usarlo**:

- Libros, manuales de entrenamiento, códigos legales o artículos académicos, donde una sola línea o dato extraído depende estrictamente del contexto general del capítulo o sección.

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Splitter para documentos padre (chunks grandes)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

# Splitter para documentos hijo (chunks pequeños para embedding)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

# Vector store para los chunks pequeños
vectorstore = Chroma(
    collection_name="parent_docs",
    embedding_function=OpenAIEmbeddings()
)

# Almacenamiento para documentos padre
store = InMemoryStore()

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# Agregar documentos
retriever.add_documents(documents)
```

## 5. SelfQueryRetriever

Muchas bases de datos vectoriales almacenan metadatos estructurados junto con los vectores de texto (ej. fecha, autor, categoría, calificación). Cuando un usuario hace una pregunta como: _"¿Cuáles fueron las películas de acción estrenadas después de 2020 que hablan de Inteligencia Artificial?"_, un recuperador normal solo hará una búsqueda semántica de "Inteligencia Artificial", ignorando los filtros implícitos.

SelfQueryRetriever utiliza un LLM para separar la consulta del usuario en dos partes: una cadena de texto para la búsqueda semántica tradicional ("Inteligencia Artificial") y una consulta estructurada de metadatos (Filtros: `género == 'acción'`, `año > 2020`). Luego ejecuta la búsqueda aplicando estos filtros directamente en la base de datos.

**Cuándo usarlo**:

- Catálogos de productos, bases de conocimiento con campos temporales (ej. noticias, reportes financieros anuales) o repositorios de contenido categorizado donde los usuarios suelen acotar sus búsquedas por atributos físicos o temporales.
- Bases de datos con metadatos ricos.
- Consultas que combinan contenido y filtros.
- Sistemas que requieren búsqueda estructurada automática.

```python
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever

# Definir metadatos de los documentos
metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="El género de la película",
        type="string"
    ),
    AttributeInfo(
        name="year",
        description="El año de lanzamiento de la película",
        type="integer"
    ),
    AttributeInfo(
        name="rating",
        description="La calificación de la película (1-10)",
        type="float"
    ),
]

document_content_description = "Breve resumen de una película"

retriever = SelfQueryRetriever.from_llm(
    llm=ChatOpenAI(temperature=0),
    vectorstore=vectorstore,
    document_content_description=document_content_description,
    metadata_field_info=metadata_field_info,
)

# Consulta que se convertirá en filtros estructurados
results = retriever.invoke("películas de ciencia ficción de después de 2010 con calificación alta")
```

## 6. TimeWeightedVectorStoreRetriever

En entornos dinámicos, la información cambia rápidamente. Un recuperador tradicional basado puramente en similitud de cosenos podría devolver un documento de hace 3 años solo porque coincide semánticamente de manera perfecta, ignorando un documento de ayer que actualiza o corrige dicha información.

TimeWeightedVectorStoreRetriever utiliza un algoritmo de puntuación combinado: **Similitud Semántica + Decaimiento Temporal**. La frescura de un documento altera su prioridad. Además, LangChain implementa esto basándose a menudo en el _tiempo desde el último acceso_, lo que significa que los documentos consultados con frecuencia se mantienen "vivos" y relevantes, mientras que los obsoletos pierden peso.

**Cuándo usarlo**:

- Canales de noticias, sistemas de notas internas de empresas en constante evolución, hilos de correos electrónicos corporativos o bitácoras de eventos en tiempo real.

```python
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from datetime import datetime, timedelta

tw_retriever = TimeWeightedVectorStoreRetriever(
    vectorstore=vectorstore,
    decay_rate=0.999,  # Qué tan rápido "olvida" documentos antiguos
    k=5
)

# Los documentos más antiguos tendrán menos peso
yesterday = datetime.now() - timedelta(days=1)
tw_retriever.add_documents([Document(page_content="Noticia vieja")], timestamps=[yesterday])
tw_retriever.add_documents([Document(page_content="Noticia nueva")])
```

## 7. Técnicas avanzadas

### Retrieval con Reranking

Los modelos de embeddings bi-encoders (como los usados en bases vectoriales) sacrifican algo de precisión a cambio de una velocidad de búsqueda masiva. No entienden bien la relación fina entre la pregunta y la respuesta.

Esta estrategia consiste en realizar una primera recuperación "sucia" o amplia (ej. extraer los mejores 25 documentos usando embeddings). Luego, esos 25 documentos pasan por un modelo **Cross-Encoder (Reranker)** más potente y pesado (como Cohere Rerank o BGE-Reranker) que evalúa individualmente el par (Pregunta, Fragmento) y los reordena de forma exacta. Finalmente, se envían solo los 3-5 mejores al LLM. Esto incrementa radicalmente la precisión de los fragmentos finales y permite recuperar más fragmentos en la fase 1 sin saturar al LLM.

**Cuándo usarlo**:

- Estándar de oro para sistemas RAG empresariales de producción que exigen máxima precisión en las respuestas.

```python
from langchain.retrievers.document_compressors import CohereRerank

# Primer pase: recuperar muchos documentos
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# Segundo pase: reordenar con Cohere
reranker = CohereRerank(
    model="rerank-multilingual-v2.0",
    top_n=5
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)
```

### Retrieval MMR (Maximum Marginal Relevance)

La búsqueda de similitud estándar tiende a devolver fragmentos que son extremadamente similares entre sí (redundancia). Si los primeros 4 fragmentos dicen exactamente la misma frase, habrás desperdiciado espacio en el contexto y te perderás otros puntos de vista presentes en fragmentos posicionados más abajo.

MMR optimiza simultáneamente la **relevancia** hacia la consulta y la **diversidad** entre los documentos seleccionados. Primero busca un grupo grande de candidatos (`fetch_k`) y luego selecciona de forma iterativa los documentos que aportan información nueva, penalizando a los que se parecen a los ya seleccionados, maximizando la variedad de información útil dentro de la ventana de contexto del LLM.

**Cuándo usarlo**:

- Consultas analíticas o comparativas (ej. _"¿Cuáles son los pros y contras del producto X?"_), asegurando que el contexto traiga tanto los pros como los contras, y no solo múltiples variantes de los pros.

```python
# Balancear relevancia con diversidad
mmr_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 10,
        "lambda_mult": 0.7  # Balance entre relevancia (1.0) y diversidad (0.0)
    }
)
```

## Conclusión: Guía de Síntesis para Selección

Como buena práctica, deberías empezar por una simple búsqueda semántica tradicional. Luego, a medida que identifiques los puntos débiles o necesidades específicas de tu sistema, puedes ir implementando técnicas avanzadas.

Para determinar qué técnica o combinación implementar en tu arquitectura RAG, puedes guiarte por la siguiente matriz de decisiones basada en el síntoma o necesidad de tu sistema:

| Si tu problema o necesidad es...                                                                | El Retriever / Técnica ideal es...   | Razón Técnica                                                                                      |
| :---------------------------------------------------------------------------------------------- | :----------------------------------- | :------------------------------------------------------------------------------------------------- |
| El usuario final escribe mal, usa jerga o preguntas muy cortas.                                 | **MultiQueryRetriever**              | El LLM expandirá la consulta en múltiples vertientes para asegurar el tiro.                        |
| Los documentos son muy largos y el LLM se confunde con el "relleno".                            | **ContextualCompressionRetriever**   | Extrae de forma quirúrgica solo las líneas relevantes de cada fragmento.                           |
| Necesitas buscar tanto por conceptos abstractos como por códigos exactos.                       | **EnsembleRetriever (Híbrido)**      | Combina la flexibilidad de los vectores con la rigidez exacta de BM25.                             |
| El contexto de la respuesta se pierde si el fragmento es demasiado corto.                       | **ParentDocumentRetriever**          | Indexa en porciones milimétricas, pero expone el párrafo o capítulo entero al LLM.                 |
| Las consultas contienen filtros explícitos (ej. "en el año 2023", "autor: Gómez").              | **SelfQueryRetriever**               | Traduce el lenguaje natural a filtros lógicos nativos de la base de datos.                         |
| La información caduca rápido o necesitas datos de última hora.                                  | **TimeWeightedVectorStoreRetriever** | Introduce un factor de decaimiento matemático basado en el tiempo.                                 |
| Quieres el máximo rendimiento posible en producción sin importar un ligero aumento de latencia. | **Retrieval con Reranking**          | Corrige los errores de la búsqueda vectorial pura ordenando los fragmentos con un modelo avanzado. |
| Los fragmentos recuperados repiten siempre lo mismo y omiten detalles secundarios.              | **Retrieval MMR**                    | Penaliza la redundancia matemática, forzando la inclusión de información diversa.                  |
