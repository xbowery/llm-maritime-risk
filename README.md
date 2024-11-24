# Ascent: LLM-Driven Exploration for Maritime Disruption Risk Analysis

This project was developed for the IS424 Data Mining and Business Analytics at the School of Computing and Information Systems (SCIS), Singapore Management University (SMU). It's a collaborative effort by an amazing team in partnership with [A*STAR](https://www.a-star.edu.sg/).

## Project Overview

This system combines several key components to provide end-to-end maritime risk analysis:

1. **Web Scraping**: Collection of maritime news from reputable sources
2. **Article Text Analysis**: Preprocessing and summarization of long articles 
3. **Articles Selection:**: Advanced preprocessing and deduplication of news articles
4. **Risk Categorization**: LLM and RAG-based classification of maritime risks
5. **Severity Assessment**: Analysis of risk impact and probability

## Module Documentation

Each module contains its own detailed README with specific instructions:

- [Scraping](./scraping/README.md): Web scraping implementation
- [Summarising](./summarising/README.md): Article summarization
- [Cleaning Module](./cleaning/README.md): Text deduplication
- Risk Categorization
    - [Prompting](./prompting/README.md): LLM-based classification using pre-defined categories
    - [RAG](./rag/README.md): RAG system for discovering new risk categories
- [Severity Prediction](./severityPrediction/README.md): Risk impact assessment

## Github Actions Workflow
To build out the entire proof of concept for our project, we enhanced the project by building a GitHub Actions workflow to automate the entire end-to-end process.

### Pre-requisites: 
1. Please ensure that you have `GEMINI_API_KEY` containing Google Gemini's API key and `DATABASE_CONNECTION` containing the MongoDB connection URL added to your repository's secrets.
2. Please run [`store_categories.py`](./prompting/templates/store_categories.py) once first before proceeding with the pipeline.

### Explanation of Workflow
1. Scraping - We have a module to automaticallly web scrape the websites and add the articles into the MongoDB. Thorough checks have been done to ensure duplicate articles from the same URL across multiple runs will not be added to the database.
2. Summarisation - We have a module to automatically summarise the content of the news articles.
3. Deduplication - We have a module to deduplicate the same news mentioned by different news outlets and focus only on the unique event for further processing with LLMs.
4. Category Generation - We have a module to automatically generate the risk categories from the LLM based on the news articles.
5. RAG - This module will automatically extract and discover new risk categories from the news articles which have been labelled as "Others" by the LLM initially.
6. Severity Prediction - This module will automatically predict the severity of the maritime risk based on the article.

## Results

The system demonstrates strong performance in:
- Accurate identification of duplicate articles
- Generation of meaningful risk categories
- Balanced severity assessment across different risk types
- Effective handling of maritime-specific context

## Future Work

- Enhanced prompt engineering with weighted factors
- Improved evaluation metrics for model comparison
- Integration of dynamic topic modeling
- Development of hybrid prediction systems

## Contributors

<table style="border-collapse: collapse; border: none;">
  <tr>
    <!-- Each contributor's image in a separate cell -->
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/vincentlewi">
        <img src="https://github.com/vincentlewi.png?size=100" width="80" height="80" alt="Alexander Vincent Lewi" style="border-radius:50%;"/>
      </a>
    </td>
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/xbowery">
        <img src="https://github.com/xbowery.png?size=100" width="80" height="80" alt="Cheah King Yeh" style="border-radius:50%;"/>
      </a>
    </td>
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/WiceKiwi">
        <img src="https://github.com/WiceKiwi.png?size=100" width="80" height="80" alt="Justin Dalva Wicent" style="border-radius:50%;"/>
      </a>
    </td>
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/taoxino-o">
        <img src="https://github.com/taoxino-o.png?size=100" width="80" height="80" alt="Law Tao Xin" style="border-radius:50%;"/>
      </a>
    </td>
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/Oliver2102">
        <img src="https://github.com/Oliver2102.png?size=100" width="80" height="80" alt="Oliver Loh" style="border-radius:50%;"/>
      </a>
    </td>
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/swiifttay">
        <img src="https://github.com/swiifttay.png?size=100" width="80" height="80" alt="Tay Si Yu" style="border-radius:50%;"/>
      </a>
    </td>
    <td align="center" style="min-width:80px;">
      <a href="https://github.com/yuenkm40">
        <img src="https://github.com/yuenkm40.png?size=100" width="80" height="80" alt="Yuen Kah May" style="border-radius:50%;"/>
      </a>
    </td>

  </tr>
  <tr>
    <!-- Each contributor's name in a separate cell -->
    <td align="center">
      <a href="https://github.com/vincentlewi"><sub><b>Alexander Vincent Lewi</b></sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/xbowery"><sub><b>Cheah King Yeh</b></sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/WiceKiwi"><sub><b>Justin Dalva Wicent</b></sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/taoxino-o"><sub><b>Law Tao Xin</b></sub></a>
    </td>
        <td align="center">
      <a href="https://github.com/Oliver2102"><sub><b>Oliver Loh</b></sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/swiifttay"><sub><b>Tay Si Yu</b></sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/yuenkm40"><sub><b>Yuen Kah May</b></sub></a>
    </td>

  </tr>
</table>

## Acknowledgments

Special thanks to:
- Dr. Fu Xiuju, Dr. Yin Xiao Feng and Ms. Tan Xue Lin from Institute of High Performance Computing, A*STAR
- Prof. Wang Zhaoxia from Singapore Management University