
import re


class SentenceChunker:

    def __init__(
        self,
        chunk_size: int = 5,
        chunk_overlap: int = 1
    ):

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_sentences(self, text: str) -> list[str]:

        sentences = re.split(
            r'(?<=[.!?؟])\s+',
            text.strip()
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def chunk_text(self, text: str) -> list[str]:

        sentences = self.split_sentences(text)

        chunks = []

        step = self.chunk_size - self.chunk_overlap

        for start in range(0, len(sentences), step):

            chunk_sentences = sentences[
                start:start + self.chunk_size
            ]

            if not chunk_sentences:
                break

            chunks.append(" ".join(chunk_sentences))

        return chunks

    def _split_sentence_spans(
        self,
        text: str
    ) -> list[tuple[int, int, str]]:

        spans = []

        start = 0

        for match in re.finditer(
            r'(?<=[.!?؟])\s+',
            text
        ):

            end = match.start()

            sentence = text[start:end].strip()

            if sentence:

                leading_spaces = len(text[start:end]) - len(
                    text[start:end].lstrip()
                )

                actual_start = start + leading_spaces

                spans.append((
                    actual_start,
                    end,
                    sentence
                ))

            start = match.end()

        # Add the final sentence
        sentence = text[start:].strip()

        if sentence:

            leading_spaces = len(text[start:]) - len(
                text[start:].lstrip()
            )

            actual_start = start + leading_spaces

            spans.append((
                actual_start,
                len(text.rstrip()),
                sentence
            ))

        return spans

    def _get_pages_for_span(
        self,
        start: int,
        end: int,
        page_spans: list[tuple[int, int, int]]
    ) -> list[int]:

        pages = []

        for page_number, page_start, page_end in page_spans:

            if start < page_end and end > page_start:
                pages.append(page_number)

        return pages

    def chunk_documents(
        self,
        documents: list[dict]
    ) -> list[dict]:

        if not documents:
            return []

        # Group pages belonging to the same source document
        grouped_documents = {}

        for document in documents:

            metadata = document["metadata"]

            source_key = (
                metadata.get("source"),
                metadata.get("file_type")
            )

            grouped_documents.setdefault(
                source_key,
                []
            ).append(document)

        all_chunks = []

        for grouped_docs in grouped_documents.values():

            full_text_parts = []
            page_spans = []

            current_position = 0

            for document in grouped_docs:

                text = document["text"].strip()

                if not text:
                    continue

                # Add a separator between pages
                separator = "\n\n" if full_text_parts else ""

                current_position += len(separator)

                page_start = current_position
                page_end = page_start + len(text)

                page_number = document["metadata"].get("page")

                if page_number is not None:

                    page_spans.append((
                        page_number,
                        page_start,
                        page_end
                    ))

                full_text_parts.append(text)

                current_position = page_end

            full_text = "\n\n".join(full_text_parts)

            if not full_text:
                continue

            sentences = self._split_sentence_spans(
                full_text
            )

            step = self.chunk_size - self.chunk_overlap

            base_metadata = dict(
                grouped_docs[0]["metadata"]
            )

            for chunk_index, start in enumerate(
                range(0, len(sentences), step),
                start=1
            ):

                chunk_sentences = sentences[
                    start:start + self.chunk_size
                ]

                if not chunk_sentences:
                    break

                chunk_text = " ".join(
                    sentence[2]
                    for sentence in chunk_sentences
                )

                # Find all pages referenced by this chunk
                chunk_pages = []

                for sentence_start, sentence_end, _ in chunk_sentences:

                    pages = self._get_pages_for_span(
                        sentence_start,
                        sentence_end,
                        page_spans
                    )

                    for page in pages:

                        if page not in chunk_pages:
                            chunk_pages.append(page)

                chunk_metadata = dict(base_metadata)

                if chunk_pages:

                    chunk_metadata["pages"] = chunk_pages

                    chunk_metadata["page"] = (
                        chunk_pages[0]
                        if len(chunk_pages) == 1
                        else None
                    )

                chunk_metadata["chunk_index"] = chunk_index

                all_chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })

        return all_chunks
