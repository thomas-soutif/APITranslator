import os

import deepl

from ._config import managed_languages_DEEPL
from ._baseclass import APITranslator
from dotenv import load_dotenv

from .Exceptions import DeepLAuthKeyNotSetException, DeepLAuthKeyWrongException, DeepLLanguageTargetNotManagedException


class DeepLTranslator(APITranslator):
    translator_object = None
    target_language_full = None
    source_language = None

    def __init__(self, target_language_full: str, source_language: str):
        self.target_language_full = target_language_full.upper()
        self.source_language = source_language
        self.check_if_language_managed()

    def _auth_from_env_file(self):
        """
        Load the KEY_DEEPL_API in the .env file to authentificate you on the DeepL API.
        :return:
        """
        load_dotenv()
        if not (os.getenv("KEY_DEEPL_API")):
            raise DeepLAuthKeyNotSetException(
                "The Auth key for DeepL was not found in the .env file, please set it as 'KEY_DEEPL_API'")
        self.translator_object = deepl.Translator(os.getenv("KEY_DEEPL_API"))
        self.check_auth(
            "The authentification key set in the .env is wrong, please check it, or use auth(key_deepl_api) to set it manually in your object.")
        return

    def auth(self, key_deepl_api=None):
        """
        Authentificate with a DeepL API pass directly in this function. If nothing pass, will try to load from the env file.
        :return:
        """
        if not key_deepl_api:
            return self._auth_from_env_file()
        self.translator_object = deepl.Translator(key_deepl_api)
        self.check_auth("The authentification key passed is wrong, please check it.")

    def translate(self, text_to_translate: str):
        """
        Translate a text with DeepL to the specified target language.
        :param text_to_translate:
        :param source_language:
        :param target_language:
        :return: The text translated
        """
        self.check_auth()
        if self.check_if_language_can_be_formal():

            result = self.translator_object.translate_text(text_to_translate,
                                                           target_lang=self.get_target_language_key(),
                                                           formality="more", preserve_formatting=True)
        else:
            result = self.translator_object.translate_text(text_to_translate,
                                                           target_lang=self.get_target_language_key(),
                                                           preserve_formatting=True)
        return result.text

    def check_auth(self, message_error=None):
        """
        Check if the authentification for the DeepL API is correct. For more information on how to setup it, visit the DeepL Api Website
        :return: An exeception if the check failed
        """
        if not message_error:
            message_error = "Authentification failed. Please use the method auth() before trying anything else."

        if not self.translator_object:
            raise DeepLAuthKeyNotSetException("Authentification failed because not set.Please use the method auth() before trying anything else.")
        try:
            self.translator_object.get_usage()
        except deepl.exceptions.AuthorizationException:
            raise DeepLAuthKeyWrongException(message_error)
        except Exception as e:
            raise e

    def managed_languages(self):
        """
        Return a list of the languages managed by the module for DeepL. It can be configure in the _config.py file
        :return: A dict that contains the language and his target_language named from the DeepL API point of view
        """

        final_dict = {}
        for lang in managed_languages_DEEPL:
            final_dict.update({lang["name"].upper(): lang["language"]})
        return final_dict

    def check_if_language_managed(self):
        """
        Check if the language target name (for example French) is managed by the module
        :param language_target_name:
        :return:
        """
        if not self.managed_languages().get(self.target_language_full.upper(), "").upper():
            raise DeepLLanguageTargetNotManagedException(
                f"The language {self.target_language_full} is not managed by the "
                f"DeepL Module. Please add it to the configuration file "
                f"'_config.py' in the variable 'managed_languages_DEEPL'. The list of language managed is {list(self.managed_languages().keys())}")

    def check_if_language_can_be_formal(self):
        """
        Check of the language can have translations with formal form
        :return: True, or false
        """
        for lang in managed_languages_DEEPL:
            if lang["name"].upper() == self.target_language_full.upper():
                if lang["supports_formality"] == False:
                    return False
                else:
                    return True

        raise Exception("Could not find the supports_formality key in the _config.py file for the "
                        "managed_languages_DEEPL variable, abort")

    def get_target_language_key(self):
        """
        Get the key name of the target language key managed by the module. For example, the key of "French" is "FR"
        :param language_target_name:
        :return:
        """
        self.check_if_language_managed()
        return self.managed_languages().get(self.target_language_full)

    def get_module_api(self) -> str:
        return "DEEPL"
