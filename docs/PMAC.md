
# Pre-trained Model Assisted Compiler (PMAC)

A **Pre-trained Model Assisted Compiler** (PMAC) is a concept that uses large [multimodal language models](https://en.wikipedia.org/wiki/Multimodal_learning) (MLLMs) to enhance the compilation process. This concept aims to bring compilable [computer language](https://en.wikipedia.org/wiki/Computer_language) closer to [natural language](https://en.wikipedia.org/wiki/Natural_language) while respecting the syntax and structure established by programming languages.

## History

The emergence of [Transformers](https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)), introduced by [Google](https://en.wikipedia.org/wiki/Google) in 2017, radically changed the technological landscape, particularly in the field of [natural language processing](https://en.wikipedia.org/wiki/Natural_language_processing). These models paved the way for significant advances, disrupting traditional methods of linguistic interaction. In 2022, [OpenAI](https://en.wikipedia.org/wiki/OpenAI) launched [ChatGPT](https://en.wikipedia.org/wiki/ChatGPT), which marked a major turning point by establishing new benchmarks in automated dialogue and human-machine interaction.

Among the innovations that followed, [LangChain](https://www.langchain.com/), introduced in 2023, enabled developers to integrate advanced language models into software applications. This development simplified the creation of conversational applications and opened the door to widespread use of AI in traditional programming contexts.

In parallel, 2023 saw [GitHub](https://en.wikipedia.org/wiki/GitHub) introduce [Copilot](https://en.wikipedia.org/wiki/GitHub_Copilot), an AI assistant that suggests contextual code, revolutionizing developer productivity and the coding process.

In this context of rapid innovation, the integration of artificial intelligence into a multitude of domains — including the compilation process — becomes evident. In 2024, the PMAC concept was born in Lyon, designed by a passionate team: Emmanuel Batt, Léandre Ramos, William Jolivet, and Merlin Devillard. In parallel, [Meta](https://en.wikipedia.org/wiki/Meta_Platforms) explored a similar approach with the development of its [LLM Compiler](https://arxiv.org/abs/2407.02524).

## Core Principle

With the emergence of artificial intelligence and the continuous evolution of language models — particularly multimodal models — NLP ([Natural Language Processing](https://en.wikipedia.org/wiki/Natural_language_processing)) capabilities have improved considerably. This advance allows us to re-evaluate the traditional stages of compilation by integrating a deeper, contextual understanding of programming languages.

In programming, a compiler is a tool that translates a [programming language](https://en.wikipedia.org/wiki/Programming_language) into [machine language](https://en.wikipedia.org/wiki/Machine_code), enabling computers to execute instructions. Programming languages vary in their level of abstraction, ranging from [low-level languages](https://en.wikipedia.org/wiki/Low-level_programming_language), close to the hardware architecture (machine code), to [high-level languages](https://en.wikipedia.org/wiki/High-level_programming_language), designed to be more abstract and human-readable.

The PMAC concept uses MLLMs to translate code containing clearer, more concrete expressions. This approach delegates the handling of ambiguities to the PMAC, enabling the management of aspects that traditional compilers could not previously process. This provides a more precise interpretation of programmatic operations, allowing the emergence of more nuanced and complex functions.

## Advantages and Disadvantages

| **Advantages** | **Disadvantages** |
|---|---|
| **Input flexibility:** Functions can be specified in natural language, enabling the execution of complex actions that would otherwise be difficult or impossible to achieve with traditional machine instructions. | **Slower compilation time:** The use of MLLMs can result in longer compilation times compared to traditional methods. |
| **Variety of implementation strategies:** The PMAC compiler can generate various types of implementation strategies, facilitating the integration of different execution modes tailored to the user's specific needs. | **Higher cost:** API calls to models or their storage can incur significant additional costs. |
| **Code optimization:** Thanks to the vast knowledge of LLMs regarding code, PMAC effectively integrates optimization techniques, improving the performance of compiled code through a deep understanding of underlying structures and logic. | **Model imperfections:** Models may present errors or divergences, posing potential risks to code reliability. |