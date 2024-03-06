from transformers import pipeline
import sentences

class IndianFoodChatbot:

    def __init__(self):
        self.classifier = pipeline(task="text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.emotion_scores = {
            "anger": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "neutral": 0,
            "sadness": 0,
            "surprise": 0
        }

    def get_highest_score(self):
        return max(self.emotion_scores, key=self.emotion_scores.get)

    def chat(self):
        while True:
            user_input = input("You: ")
            self.emotion_scores = {k: 0 for k in self.emotion_scores}
            self.emotion_scores[self.classifier(user_input, return_all_scores=True)[0]["label"]] = 1
            print(f"Bot: I can see that you are feeling {self.get_highest_score()}.")