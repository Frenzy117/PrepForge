import os
from playwright.async_api import async_playwright
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from backend.PromptRepository import jobReaderTemplate

@tool
async def get_job_summary(job_link: str) -> str:
    """
    Extracts structured information from a job posting at the provided URL.

    Args:
        job_link (str): The URL of the job posting.

    Returns:
        str: A structured summary of the job posting's key details.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url=job_link)
        await page.wait_for_selector(".jobsearch-JobComponent", timeout=15000)

        description = (await page.locator('.jobsearch-JobComponent').text_content()).strip() or None

    await browser.close()

    # description = await get_job_elements(job_link)
    llm_model = ChatMistralAI(api_key=os.getenv("MISTRAL_API_KEY"))
    final_prompt = jobReaderTemplate.invoke({"description":description})
    chat_result = llm_model.invoke(final_prompt)

    return chat_result.content