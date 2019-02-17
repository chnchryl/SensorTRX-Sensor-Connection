class DataChunker:

    def __init__(self, message, max_chars=20):

        assert max_chars >= 2
        
        self.max_chars = max_chars
        self.message = message

    def generate_token_list(self):
        
        tokens = []
        word = ["0:"]
        size = self.max_chars - 2
        
        for c in self.message:

            if len(word) == size:
                tokens.append("".join(word))
                word_start = str(len(tokens)) + ":"

                size = self.max_chars - len(word_start)
                word = [word_start]

            word.append(c)

        tokens.append("".join(word))

        return tokens
