"""Mail class to send mails via SMTP."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import config
from .logger import logger
from .mail_template import mail_template

class Mail:
    """Provide a method to send mails via SMTP."""

    def __init__(self) -> None:
        """Initialize the mails sender."""
        self.__host = config.SMTP_HOST.strip()
        self.__port = config.SMTP_PORT
        self.__sender = config.SMTP_FROM.strip()
        self.__to = config.SMTP_TO.strip()
        self.__username = config.SMTP_USERNAME
        self.__password = config.SMTP_PASSWORD

    def send(self, subject: str, message: str) -> None:
        """Send a mail.

        Parameters
        ----------
        subject : str
            Subject.
        message : str
            Message.
        """
        try:
            if not self.__sender:
                logger.warning('Correo no enviado. Remitente no establecido.')
                return

            if not self.__to:
                logger.warning(
                    'Correo no enviado. Destinatario no establecido.'
                )
                return

            if not subject or not message:
                logger.warning(
                    'Correo no enviado. El asunto y el mensaje son requeridos.'
                )
                return

            msg = MIMEMultipart()
            msg['From'] = self.__sender
            msg['To'] = self.__to
            msg['Subject'] = subject
            body = mail_template.replace('{{message}}', message)
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.__host, self.__port) as server:
                server.set_debuglevel(False)
                if self.__username and self.__password:
                    server.login(self.__username, self.__password)
                server.sendmail(self.__sender, self.__to, msg.as_string())

            logger.success(f'Correo enviado correctamente a {self.__to!r}')
        except Exception as e:
            logger.error(f'No se pudo enviar el correo: {str(e)}')
