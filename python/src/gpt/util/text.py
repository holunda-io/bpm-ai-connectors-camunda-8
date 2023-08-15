import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')


def remove_stop_words(sentence, separator=' ', max_n_result_words: int = 6):
    stop_words = set(stopwords.words('english') + stopwords.words('german'))

    # Split the sentence into individual words
    words = sentence.split()

    # Use a list comprehension to remove stop words
    filtered_words = [word for word in words if word not in stop_words]

    # Join the filtered words back into a sentence
    return separator.join(filtered_words[:max_n_result_words])
