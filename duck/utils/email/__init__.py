"""
A reusable utility module for sending emails via SMTP, suitable for integration in any Python project or library.
Provides a generic Email class for any SMTP server and a Gmail subclass for Gmail-specific settings, 
with both synchronous and asynchronous implementations.

Note:
    You should load sensitive credentials (like SMTP usernames and passwords) securely,
    for example using environment variables or a .env file:
        from dotenv import load_dotenv; load_dotenv()
    Or by passing them directly as arguments to class constructors.

Author: digreatbrian
"""

import smtplib
from typing import List, Optional, Tuple

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from duck.shortcuts import render

# For async sending
try:
    import aiosmtplib
except ImportError:
    aiosmtplib = None


class Email:
    """
    Compose and send emails via any SMTP server (sync and async).

    This class provides a general interface to create an email and send it using any SMTP server.
    It supports sending to a single recipient and optionally multiple recipients via CC or BCC.

    Attributes:
        smtp_host (str): SMTP server hostname (e.g., "smtp.gmail.com").
        smtp_port (int): SMTP server port (e.g., 465 for SSL).
        username (str): SMTP server login username (usually the sender's email).
        password (str): SMTP server login password or app password.
        use_ssl (bool): Whether to use SSL for SMTP (default True).
        from_addr (str): The sender's email address.
        name (str): The sender's display name.
        to (str): The main recipient's email address.
        subject (str): The subject of the email.
        body (str): The HTML content of the email.
        recipients (Optional[List[str]]): Additional recipient emails for CC/BCC.
        use_bcc (bool): If True, recipients are BCCed; otherwise, they are CCed.
        is_sent (bool): True if the email was sent successfully.

    Example:
        email = Email(
            smtp_host="smtp.mailgun.org",
            smtp_port=465,
            username="your@mail.com",
            password="yourpassword",
            from_addr="your@mail.com",
            name="Your Name",
            to="recipient@example.com",
            subject="Hello from Mailgun",
            body="<b>Welcome!</b>",
        )
        email.send()
        # or for async:
        await email.async_send()
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        name: str,
        to: str,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
        use_bcc: bool = True,
        use_ssl: bool = True,
    ):
        """
        Initialize a generic Email instance.

        Args:
            smtp_host: SMTP server host.
            smtp_port: SMTP server port.
            username: SMTP login username (email address).
            password: SMTP login password or app password.
            from_addr: Sender's email address.
            name: Sender's display name.
            to: Main recipient's email address.
            subject: Subject of the email.
            body: HTML content of the email.
            recipients: List of additional recipient emails for CC/BCC (optional).
            use_bcc: If True, use BCC for recipients; otherwise, use CC.
            use_ssl: Whether to use SSL for SMTP (default True).
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username or from_addr
        self.password = password
        self.from_addr = from_addr
        self.name = name
        self.to = to
        self.subject = subject
        self.body = body
        self.recipients = recipients or []
        self.use_bcc = use_bcc
        self.use_ssl = use_ssl
        self.is_sent = False

    def _build_message(self) -> Tuple[MIMEMultipart, List[str]]:
        """
        Build the MIME email message and return (msg, all_recipients).

        Returns:
            Tuple: (MIMEMultipart message, list of all recipient addresses)
        """
        msg = MIMEMultipart()
        msg['From'] = formataddr((self.name, self.from_addr))
        msg['To'] = self.to
        msg['Subject'] = self.subject

        if self.recipients:
            if self.use_bcc:
                all_recipients = [self.to] + self.recipients
            else:
                msg["Cc"] = ", ".join(self.recipients)
                all_recipients = [self.to] + self.recipients
        else:
            all_recipients = [self.to]

        msg.attach(MIMEText(self.body, 'html'))
        return msg, all_recipients

    def send(self) -> None:
        """
        Send the composed email using the specified SMTP server (synchronously).

        Raises:
            Exception: If sending fails due to authentication or network errors.
        """
        msg, all_recipients = self._build_message()
        
        # Send the email securely via SMTP_SSL or plain SMTP
        if self.use_ssl:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(self.from_addr, all_recipients, msg.as_string())
        else:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_addr, all_recipients, msg.as_string())
        self.is_sent = True

    async def async_send(self) -> None:
        """
        Send the composed email using the specified SMTP server (asynchronously).

        Requires:
            aiosmtplib (pip install aiosmtplib)

        Raises:
            ImportError: If aiosmtplib is not installed.
            Exception: If sending fails due to authentication or network errors.
        """
        if aiosmtplib is None:
            raise ImportError("aiosmtplib is required for async email sending. Install with 'pip install aiosmtplib'.")

        msg, all_recipients = self._build_message()
        
        # aiosmtplib expects the message as a string
        if self.use_ssl:
            await aiosmtplib.send(
                message=msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                use_tls=True,
                sender=self.from_addr,
                recipients=all_recipients,
            )
        else:
            await aiosmtplib.send(
                message=msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                start_tls=True,
                sender=self.from_addr,
                recipients=all_recipients,
            )
        self.is_sent = True

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}'
            f' from="{self.from_addr}"'
            f' to="{self.to}"'
            f' host="{self.smtp_host}">'
        )
    
    def __str__(self):
        return (
            f'<{self.__class__.__name__}'
            f' from="{self.from_addr}"'
            f' to="{self.to}"'
            f' host="{self.smtp_host}">'
        )



class Gmail(Email):
    """
    Compose and send emails specifically via Gmail's SMTP server.

    This is a convenience subclass of Email that pre-fills Gmail's SMTP configuration.
    You must still provide your Gmail address and app password.

    Example:
        gmail = Gmail(
            username="your@gmail.com",
            password="your_app_password",
            from_addr="your@gmail.com",
            name="Your Name",
            to="recipient@example.com",
            subject="Hello from Gmail",
            body="<b>Welcome!</b>",
        )
        gmail.send()
        # or for async:
        await gmail.async_send()
    """

    def __init__(
        self,
        username: str,
        password: str,
        from_addr: str,
        name: str,
        to: str,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
        use_bcc: bool = True,
        use_ssl: bool = True,
    ):
        """
        Initialize a Gmail email instance with Gmail's SMTP settings.

        Args:
            username: Gmail address.
            password: Gmail app password.
            from_addr: Gmail address (same as username).
            name: Sender's display name.
            to: Main recipient's email address.
            subject: Subject of the email.
            body: HTML content of the email.
            recipients: List of additional recipient emails (optional).
            use_bcc: If True, use BCC for recipients; otherwise, use CC.
            use_ssl: Whether to use SSL for SMTP (default True).
        """
        super().__init__(
            smtp_host="smtp.gmail.com",
            smtp_port=465,
            username=username,
            password=password,
            from_addr=from_addr,
            name=name,
            to=to,
            subject=subject,
            body=body,
            recipients=recipients,
            use_bcc=use_bcc,
            use_ssl=use_ssl,
        )
