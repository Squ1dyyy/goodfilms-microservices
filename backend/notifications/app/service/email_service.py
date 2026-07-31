from notifications.config import config
from email.message import EmailMessage
import aiosmtplib


async def _send_email(
    _to: str,
    subject: str,
    content: str,
):
    message = EmailMessage()
    message["From"] = config.email_login
    message["To"] = _to
    message["Subject"] = subject

    message.set_content(content, subtype="html")

    smtp = aiosmtplib.SMTP(
        hostname=config.smtp_host,
        port=config.smtp_port,
        start_tls=True,
    )

    async with smtp:
        await smtp.login(config.email_login, config.email_password)
        await smtp.send_message(message)


async def send_verification(
    recipient: str,
    code: int,
):
    subject = "Подтверждение регистрации"
    content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f4f5f7; margin: 0; padding: 0; }}
            .wrapper {{ width: 100%; background-color: #f4f5f7; padding: 40px 0; }}
            .card {{ max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); overflow: hidden; }}
            .header {{ background-color: #4F46E5; padding: 32px; text-align: center; }}
            .header h1 {{ color: #ffffff; font-size: 24px; margin: 0; }}
            .content {{ padding: 40px 32px; text-align: center; color: #334155; }}
            .content p {{ font-size: 16px; line-height: 1.5; margin: 0 0 24px 0; }}
            .code-box {{ background-color: #F1F5F9; border-radius: 8px; padding: 16px; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #1E293B; display: inline-block; margin: 10px 0 30px 0; border: 1px dashed #CBD5E1; }}
            .footer {{ background-color: #F8FAFC; padding: 24px 32px; text-align: center; font-size: 13px; color: #94A3B8; border-top: 1px solid #E2E8F0; }}
            .footer a {{ color: #4F46E5; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="card">
                <div class="header"><h1>Добро пожаловать!</h1></div>
                <div class="content">
                    <p>Спасибо за регистрацию. Для подтверждения вашего профиля используйте этот одноразовый код активации:</p>
                    <div class="code-box">{code}</div>
                    <p style="font-size: 14px; color: #64748B; margin: 0;">
                        Код действителен в течение 15 минут.<br>
                        Если вы не запрашивали этот код, просто проигнорируйте это письмо.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 Ваша Компания. Все права защищены.</p>
                    <p>Возникли вопросы? <a href="mailto:support@yourcompany.com">Напишите в поддержку</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return await _send_email(recipient, subject, content)


async def password_reset(
    recipient: str,
    token: str,
):
    subject = "Смена пароля"

    reset_link = f"https://yourdomain.com/reset-password?token={token}"

    content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f4f5f7; margin: 0; padding: 0; }}
            .wrapper {{ width: 100%; background-color: #f4f5f7; padding: 40px 0; }}
            .card {{ max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); overflow: hidden; }}
            .header {{ background-color: #EF4444; padding: 32px; text-align: center; }}
            .header h1 {{ color: #ffffff; font-size: 24px; margin: 0; }}
            .content {{ padding: 40px 32px; text-align: center; color: #334155; }}
            .content p {{ font-size: 16px; line-height: 1.5; margin: 0 0 24px 0; }}
            .btn {{ display: inline-block; background-color: #EF4444; color: #ffffff !important; padding: 14px 28px; font-weight: 600; text-decoration: none; border-radius: 8px; margin: 10px 0 25px 0; box-shadow: 0 2px 5px rgba(239, 68, 68, 0.2); }}
            .footer {{ background-color: #F8FAFC; padding: 24px 32px; text-align: center; font-size: 13px; color: #94A3B8; border-top: 1px solid #E2E8F0; }}
            .footer a {{ color: #EF4444; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="card">
                <div class="header">
                    <h1>Сброс пароля</h1>
                </div>
                <div class="content">
                    <p>Мы получили запрос на восстановление доступа к вашему аккаунту. Нажмите на кнопку ниже, чтобы задать новый пароль:</p>

                    <a href="{reset_link}" class="btn" target="_blank">Восстановить пароль</a>

                    <p style="font-size: 14px; color: #64748B; margin: 0; line-height: 1.4;">
                        Ссылка действительна в течение 15 минут.<br>
                        Если вы не отправляли этот запрос, ваш пароль останется прежним — просто удалите это письмо.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 GoodFilms. Все права защищены.</p>
                    <p>Нужна помощь? <a href="mailto:goodfilms@gmail.com">Служба поддержки</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return await _send_email(recipient, subject, content)


async def welcome_message(recipient: str):
    subject = "Успешная активация аккаунта!"
    content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f4f5f7; margin: 0; padding: 0; }}
            .wrapper {{ width: 100%; background-color: #f4f5f7; padding: 40px 0; }}
            .card {{ max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); overflow: hidden; }}
            .header {{ background-color: #10B981; padding: 32px; text-align: center; }}
            .header h1 {{ color: #ffffff; font-size: 24px; margin: 0; }}
            .content {{ padding: 40px 32px; text-align: center; color: #334155; }}
            .content h2 {{ font-size: 20px; color: #1E293B; margin: 0 0 16px 0; font-weight: 600; }}
            .content p {{ font-size: 16px; line-height: 1.6; margin: 0 0 24px 0; color: #475569; }}
            .btn {{ display: inline-block; background-color: #10B981; color: #ffffff !important; padding: 14px 28px; font-weight: 600; text-decoration: none; border-radius: 8px; margin: 10px 0 10px 0; }}
            .footer {{ background-color: #F8FAFC; padding: 24px 32px; text-align: center; font-size: 13px; color: #94A3B8; border-top: 1px solid #E2E8F0; }}
            .footer a {{ color: #10B981; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="card">
                <div class="header">
                    <h1>Вы с нами! 🎉</h1>
                </div>
                <div class="content">
                    <h2>Ваш аккаунт успешно создан</h2>
                    <p>Теперь вам открыт полный доступ ко всем функциям нашей платформы. Мы рады, что вы присоединились к нам!</p>

                    <a href="http://localhost:8000/docs" class="btn" target="_blank">Войти в личный кабинет</a>
                </div>
                <div class="footer">
                    <p>© 2026 GoodFilms. Все права защищены.</p>
                    <p>Рады помочь: <a href="mailto:goodfilms@gmail.com">goodfilms@gmail.com</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return await _send_email(recipient, subject, content)
