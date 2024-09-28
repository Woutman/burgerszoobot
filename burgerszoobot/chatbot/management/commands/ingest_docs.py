import json
from django.core.management.base import BaseCommand
from chatbot.services.retrieval import ingest_document


class Command(BaseCommand):
    help = 'Ingest documents into persistent ChromaDB'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing documents')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                documents = json.load(file)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading file: {e}"))
            return

        for i, doc in enumerate(documents):
            try:
                ingest_document(document_id=str(i), document_text=doc)
                self.stdout.write(self.style.SUCCESS(f"Successfully ingested document {i}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error ingesting document {i}: {e}"))
