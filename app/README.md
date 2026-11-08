# A Comprehension-Based Web App

This is a forkable web player that allows anyone to develop and share their own comprehension-based language course.

## Run it locally

You need Node.js 22.

From `app/`:

```bash
npm install
npm run dev
```

Then open [http://localhost:8080](http://localhost:8080).

The first time you clone, `npm install` is required. After that, `npm run dev` is enough.

The lesson player starts on that URL. There is no login step and no extra env file for local use.

## What this project solves

A course on this model separates into four tasks:

1. Writing the lessons: which meanings are pictured, in what order, and how the repetitions are spaced for the particular language involved.
2. Producing the pictures and the recordings.
3. \* Building the software that presents each picture with its audio.
4. \* Distributing the finished course.

This repository gives you number 3 and 4 on a plate. It is an open-source web application that plays a comprehension sequence. You supply the lessons and the content. A lesson is a list of plates, each an image file and an audio file, in an order that spaces the returns of each plate and avoids playing the same plate twice in a row. Filenames are opaque. The screen shows the picture and plays the recording, so the picture remains the source of the meaning. 

In this repository, the course pipeline (`course-pipeline` skill) does tasks 1 and 2. `scripts/export_course.py` copies a finished lesson into `public/courses/` and writes its manifest to `src/lesson/content/`. Every manifest there appears as a new step in its level. Generated lessons are gitignored. The Spanish demo lesson stays tracked.

## Why this exists

No Winitz-style course has been published for Latin: pictures sequenced with spoken Latin, meaning carried by the picture, speech and translation left out of the early lessons.

The best available option today is *Lingua Latina per se Illustrata* (Hans H. Ørberg), an inductive reader that uses the direct method. But this approach is first and foremost a text-based approach, not an audio-visual one. Latin marginal glosses and a few illustrations carry the sense for dense paragraphs. It is built for a learner who can follow connected prose, and it moves at the pace of that prose. These are innapropriate assumption for a beginner. And in this way, the reader is properly designed for someone who already has some exposure to the language. To improve _LLPSI_, a comprehension sequence of the Winitz kind could sit just ahead of each chapter, so the forms and the vocabulary are already understood as sound and meaning when the prose begins. This is actually not too far of from Winitz's own curriculum, which includes a second volume of reading materials.

Randall Buth has used this very design for Koine Greek and Biblical Hebrew. *Living Koine Greek* and *Living Biblical Hebrew* volumes 1 are entirely pictures with audio descriptions in the target language. The learner progresses from single words through phrases to short story sequences. The second and third volumes begin to encoroporate reading and New Testament passages. In the classroom Buth pairs this with Asher's Total Physical Response. He describes the design in [this interview](https://www.biblicallanguagecenter.com/interview-randall-buth/). The picture sequence is the piece this project is meant to make buildable for Latin--or any other language a person wants.

The model adopted here is popularly known as the "comprehension approach" to second language acquisition. This approach relies on the observation that children pass through a long silent period in which they map utterances onto the world arround them, with speach occuring on the child's own timelines without any explicit grammar instruction. The theory this course relies on asserts that second language acquisition works the same way. [Harris Winitz](https://en.wikipedia.org/wiki/Harris_Winitz) argued that adult instruction should keep the same order, comprehension before production, and he built a curriculum on the claim: The Learnables, from International Linguistics Corporation. (The research program is collected in *The Comprehension Approach to Foreign Language Instruction* [Newbury House, 1981].) While picture-and-audio courses already existed, the Learnables reoriented the format according to this specific acquisition theory.

Why not just use Rosetta Stone? In the early 1970s Winitz presented four pictures with one recorded sentence and asked the learner to choose the match. The Learnables left that design in 1976 and opted for the one picture with one utterance, removing the guess-work for the learner. This aligned more closely with the theoretical underpinnings of the comprehension based approach. 

When Rosetta Stone was developed in the early 1990s, Allen Stoltzfus—who knew The Learnables and the 1981 volume—contacted Winitz with his idea for a software based curriculum. Rosetta Stone shipped the four-picture format The Learnables had dropped. It then adopted different theoretical underpinnings, closer to Paul Nation's "Four Strands" methodology.

Further reading: Winitz, H. (Ed.). (1981). *The Comprehension Approach to Foreign Language Instruction*. Newbury House. Winitz's own comparison of formats is on the [Learnables FAQ](https://learnables.com/faqs/).
