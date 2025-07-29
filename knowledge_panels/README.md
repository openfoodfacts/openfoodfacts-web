# How to Write a New Knowledge Panel

Knowledge panels are an important way to provide users with concise and relevant information about various food-related topics, such as ingredients, additives, labels, and nutrients. This guide outlines how to create new knowledge panels using the `world-en.yml` files and provides guidelines for content.

## File Structure and Naming

Knowledge panels are organized into directories based on their category (e.g., `ingredients`, `additives`, `labels`, `nutrients`, `categories`). Within each category, there's an `off` (Open Food Facts) or `obf` (Open Beauty Facts) subdirectory, and inside that, you'll find the `world-en.yml` file.

When adding a new knowledge panel, you'll be adding a new entry to the relevant `world-en.yml` file.

## Format of a Knowledge Panel Entry

Each entry in the `world-en.yml` file follows a YAML format. Here's a general structure:

```yaml
"en:your-panel-identifier":
  content: |-
    - ***What it is:*** [Brief description of the item]
    - ***Why it's used:*** [If applicable, explain its purpose or common uses]
    - ***Types:*** [If applicable, list different types or variations]
    - ***Concerns:*** [Outline any potential health, environmental, or other concerns. Be factual and cite sources where possible.]
    - ***Sources:*** [List your sources here, preferably with links, e.g., [WHO](https://www.who.int/...)]
```

**Key elements:**

*   **`"en:your-panel-identifier"`:** This is the unique key for your knowledge panel. It should match an entry in the relevant Open Food Facts taxonomy.
    *   It should be in English (`en:` prefix).
    *   Use lowercase letters and hyphens for spaces (e.g., `en:corn-syrup`, `en:e202`).
    *   Make it descriptive and relevant to the content.
*   **`content: |-`**: This indicates that the following text block is the content for the panel. The `|-` preserves newlines.
*   **List format (`- `):** Each point within the content should start with a hyphen and a space. This creates a bulleted list in the displayed panel.
*   **Markdown for emphasis:** You can use Markdown for formatting, like `***Bold Italic***` for section headers (e.g., `***What it is:***`).
*   **Brevity:** Keep the information concise and to the point. Users are often looking for quick summaries.
*   **Clarity:** Use clear and simple language. Avoid jargon where possible, or explain it if necessary.

## Guidelines for Content

### 1. Sourcing and Accuracy

*   **Reliable Sources:** Always base your information on credible and authoritative sources. Examples include:
    *   World Health Organization (WHO)
    *   Food and Agriculture Organization (FAO)
    *   Reputable scientific studies and journals
    *   Official regulatory bodies (e.g., FDA, EFSA)
    *   Well-established non-governmental organizations (e.g., WWF for environmental concerns).
*   **Cite Your Sources:** Include a `***Sources:***` section with links to your sources. This builds trust and allows users to verify the information.
*   **Factual Information:** Ensure the information is accurate and up-to-date. If there are differing opinions or ongoing research, represent this fairly.
*   **Neutral Tone:** Present information objectively. While it's important to highlight concerns, avoid overly alarmist or biased language.

### 2. Brevity and Conciseness

*   **Get to the Point:** Knowledge panels are meant to be quick reads. Focus on the most important information.
*   **Bullet Points:** Use bullet points to break down information into digestible chunks.
*   **Short Sentences:** Prefer shorter sentences for better readability.
*   **Avoid Redundancy:** Don't repeat information unnecessarily.

### 3. Structure and Formatting (Inferred from Existing Panels)

*   **"What it is":** Almost all panels start with a brief definition or description.
*   **Contextual Information:** Depending on the item, include sections like:
    *   `***Why it's used:***` (for additives, ingredients)
    *   `***Types:***` (for ingredients with variations)
    *   `***Concerns:***` (This is a crucial section. Be specific about the nature of the concerns – health, environmental, etc.)
    *   `***Health concerns:***` (Can be a dedicated subsection if needed)
*   **Highlighting Key Information:**
    *   Use bolding (`**text**`) for emphasis on important terms or warnings (e.g., `**They do not present any known health risks**`, `**possible human carcinogen (Group 2B)**`).
*   **Clarity on Safety:** If an item is generally recognized as safe (GRAS) or has no known health risks, state that clearly. Conversely, if there are significant concerns or classifications (like IARC carcinogen groups), mention them.

### 4. Specific Panel Types - Examples from Existing Files:

*   **Additives (`knowledge_panels/additives/off/world-en.yml`):**
    *   Often include the E-number (e.g., `en:e202` for Potassium sorbate).
    *   Explain the additive's function (e.g., preservative, emulsifier, thickener).
    *   Discuss safety assessments and any known health concerns.
*   **Ingredients (`knowledge_panels/ingredients/off/world-en.yml` & `knowledge_panels/ingredients/obf/world-en.yml`):**
    *   Describe what the ingredient is and where it comes from.
    *   Explain its common uses in food or beauty products.
    *   Detail any health or environmental concerns.
    *   May include common names or how to identify it on ingredient lists.
*   **Nutrients (`knowledge_panels/nutrients/off/world-en.yml`):**
    *   Explain the role of the nutrient in the body.
    *   Mention deficiency symptoms or benefits.
    *   List good food sources.
*   **Labels (`knowledge_panels/labels/off/world-en.yml`):**
    *   Explain what the label signifies (e.g., Nutri-Score).
    *   Describe its purpose and how it works.
    *   Mention its origin and adoption.
*   **Categories (`knowledge_panels/categories/off/world-en.yml`):**
    *   Define the food category.
    *   Describe typical characteristics or ingredients.
    *   Mention cultural significance if applicable (e.g., Easter eggs).

## Steps to Add a New Panel:

1.  **Identify the Correct Category:** Determine if your panel is about an ingredient, additive, nutrient, label, or general food category.
2.  **Navigate to the `world-en.yml` file:** Go to the appropriate subdirectory (e.g., `knowledge_panels/ingredients/off/world-en.yml`).
3.  **Research Thoroughly:** Gather information from reliable sources.
4.  **Choose a Unique Identifier:** Create a clear, hyphenated identifier prefixed with `en:`.
5.  **Write the Content:** Follow the formatting and content guidelines above.
    *   Start with `content: |-`.
    *   Use bullet points (`- `) for each piece of information.
    *   Use `***Bold Italic:***` for section titles within the panel.
    *   Be concise, accurate, and cite your sources.
6.  **Add Your Entry:** Append your new panel to the end of the YAML file. Ensure correct indentation.
7.  **Review and Test:** (If possible, though not explicitly stated in the files, it's good practice) Preview how the panel would look and check for any formatting errors.

By following these guidelines, you can contribute valuable and easy-to-understand information to Open Food Facts users!


### How to generate HTML pages for additives from the Yaml page ?

Install the dependencies, then run the command with the list of directories containing the yaml files.

```bash
python3 build_html.py additives ingredients categories nutrients
```

The name of the directory must correspond to a tag type (ex: additives, ingredients, etc).
