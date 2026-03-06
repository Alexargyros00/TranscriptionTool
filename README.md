# TranscriptionTool

This project transcribes a `.m4a` file with OpenAI and saves a formatted transcript to a text file.

The flow is simple:
- split the input audio into smaller chunks with `ffmpeg`
- transcribe each chunk with Whisper
- merge the chunks back into one timestamped transcript
- send that transcript to GPT-4.1 mini so it formats speaker turns as readable lines

## Models Used

The script uses:
- `whisper-1` for speech-to-text
- `gpt-4.1-mini` for transcript formatting

Whisper does the raw transcription and returns timestamped segments. GPT-4.1 mini does not transcribe the audio; it only takes the timestamped text and rewrites it into a cleaner speaker-style transcript.

In one real run, a `1:23:13` `.m4a` file processed with Whisper and GPT-4.1 mini cost about `$0.87` in OpenAI. Treat that as an example, not a guarantee, because cost depends on the file and current OpenAI pricing.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Alexargyros00/TranscriptionTool
cd TranscriptionTool
```

2. Create an OpenAI API key from the OpenAI platform (https://developers.openai.com/). 

3. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

4. Install dependencies:

```bash
uv sync
```

## Usage

The script only accepts `.m4a` input files.

Example:

```bash
uv run .\main.py .\demo.m4a .\demo.txt
```

Or with full paths:

```bash
uv run .\main.py "C:\path\to\audio.m4a" ".\output.txt"
```

## Output

The output is a plain text file with timestamps and speaker-formatted lines (good choice also for Greek audio files), for example :

```text
[00:00:00] Speaker 1: Αυτή είναι μια γρήγορη σύνοψη για τα μοντέλα Transformer και την πλατφόρμα τεχνητής νοημοσύνης Hugging Phase.  
[00:00:07] Speaker 1: Ουσιαστικά, βλέπουμε κάτω από το καπό για να καταλάβουμε πώς ακριβώς δουλεύουν οι σημερινοί εγκέφαλοι της μηχανικής μάθησης,  
[00:00:14] Speaker 1: δίνοντάς σας τα εργαλεία να τους χρησιμοποιήσετε άμεσα, χωρίς να πνιγείτε στη θεωρία.  
[00:00:20] Speaker 1: Λοιπόν, πρώτον, πρέπει να ξέρετε ότι η αρχιτεκτονική είναι το παν εδώ και χωρίζεται σε τρεις βασικές κατηγορίες.  
[00:00:27] Speaker 1: Έχουμε τους αναλυτές, δηλαδή τα μοντέλα Encoder, που διαβάζουν όλο το κείμενο μαζί για να βγάλουν βαθύ νόημα.  
[00:00:34] Speaker 1: Μετά, περνάμε στους δημιουργούς, τα μοντέλα Decoder όπως το γνωστό μας GPT, που συντάσσουν νέο κείμενο μαντεύοντας την επόμενη λέξη.  
[00:00:43] Speaker 1: Και φυσικά, υπάρχουν τα ευρυδικά μοντέλα που τα συνδυάζουν όλα, όντας ιδανικά, για πολύπλοκες εργασίες όπως οι μεταφράσεις εγγράφων.  
[00:00:51] Speaker 1: Δεύτερον, πώς το κάνουμε πράξη.  
[00:00:54] Speaker 1: Εδώ μπαίνει στο παιχνίδι το Hugging Face.  
[00:00:56] Speaker 1: Φανταστείτε το σαν το απόλυτο plug-and-play εργαλείο, ειδικά χάρη στη λειτουργία Pipeline.  
[00:01:02] Speaker 1: Με κυριολεκτικά μία γραμμή κώδικα, κατεβάζετε έτοιμα, πανίσχυρα μοντέλα για να κάνετε τα πάντα.  
[00:01:08] Speaker 1: Από ανάλυση κειμένου, μέχρι αυτόματη περίληψη, χωρίς να χρειαστεί να εκπαιδεύσετε απολύτως τίποτα δικό σας.  
[00:01:14] Speaker 1: Είναι τρομερό.  
[00:01:15] Speaker 1: Τρίτον, και ίσως το πιο εντυπωσιακό, είναι πως η τεχνολογία των Transformers δεν περιορίζεται πια στις λέξεις.  
[00:01:22] Speaker 1: Εφαρμόζεται στην αναγνώριση ομιλίας, μεταγράφοντας ήχος-εκείμενο σε πραγματικό χρόνο,  
[00:01:27] Speaker 1: αλλά και στην όραση υπολογιστών.  
[00:01:29] Speaker 1: Εκεί, το λογισμικό παίρνει μία εικόνα και την κόβει σε μικρά τετραγωνάκια,  
[00:01:34] Speaker 1: διαβάζοντάς ακριβώς με την ίδια λογική που θα διάβαζε τις λέξεις μιας πρότασης.  
[00:01:39] Speaker 1: Συνοψίζοντας, κατανοώντας αυτές τις βασικές αρχιτεκτονικές και αξιοποιώντας έτοιμα εργαλεία,  
[00:01:44] Speaker 1: έχετε πλέον στα χέρια σας τη δύναμη να λύσετε σχεδόν οποιοδήποτε πρακτικό πρόβλημα έξυπνα και αιστραπιαία.
```

