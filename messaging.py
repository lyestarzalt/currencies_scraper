import firebase_admin.messaging as messaging


def send_localized_notification(language, current_date):
    """Sends a notification message to a language-specific topic with current date, in the appropriate language."""
    # Localized messages
    localized_titles = {
        'en': 'New Currency Rates',
        'de': 'Neue Währungskurse',
        'fr': 'Nouveaux taux de change',
        'ar': 'أسعار العملات الجديدة',
        'es': 'Nuevas tasas de cambio',
        'zh': '新的货币汇率',
    }

    localized_bodies = {
        'en': 'New rates for Dinar and other currencies are now available on {date}.',
        'de': 'Neue Kurse für Dinar und andere Währungen sind jetzt am {date} verfügbar.',
        'fr': 'Les nouveaux taux pour le Dinar et d\'autres devises sont disponibles le {date}.',
        'ar': 'الأسعار الجديدة للدينار والعملات الأخرى متاحة الآن في {date}.',
        'es': 'Nuevas tasas para el Dinar y otras monedas están disponibles el {date}.',
        'zh': '{date}现在有第纳尔和其他货币的新汇率。',
    }

    # Format the current date
    formatted_date = current_date.strftime('%Y-%m-%d')

    # Fetch localized title and body, format with the date
    title = localized_titles.get(language, localized_titles['en'])
    body = localized_bodies.get(
        language, localized_bodies['en']).format(date=formatted_date)

    # Define the notification message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=f'allDevices_{language}',
    )

    # Send the message
    response = messaging.send(message)
    print(f'Successfully sent message to {language} topic:', response)
