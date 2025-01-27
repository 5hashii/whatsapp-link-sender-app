import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.api_token = os.getenv('WHATSAPP_API_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.api_version = 'v17.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}/{self.phone_number_id}'

    def send_message(self, to_phone_number, message):
        """
        Send a WhatsApp message using the Cloud API
        :param to_phone_number: Recipient's phone number with country code (e.g., +1234567890)
        :param message: Message text to send
        :return: Response from the API
        """
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

        # Remove any spaces or special characters from phone number
        to_phone_number = ''.join(filter(str.isdigit, to_phone_number))

        data = {
            'messaging_product': 'whatsapp',
            'to': to_phone_number,
            'type': 'text',
            'text': {'body': message}
        }

        try:
            response = requests.post(
                f'{self.base_url}/messages',
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
