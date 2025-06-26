import os
import json
import re
import gradio as gr
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from rag_agent import run_agent
from db_utils import (
    get_drug_id, get_available_stock, insert_sale, update_stock,
    get_inventory_info, get_full_inventory
)

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("Missing GOOGLE_API_KEY in environment variables.")

genai.configure(api_key=api_key)
vision_model = genai.GenerativeModel("gemini-1.5-flash")

vision_prompt = """
You are a pharmacy assistant AI. Your task is to extract structured information from a handwritten prescription image.
Return only valid JSON in the following format:
{
  "medicines": [
    {
      "name": "<Extracted medicine name>",
      "frequency": "<Extracted number of doses per day (e.g., 2)>",
      "duration": "<Extracted duration in days (e.g., 5)>",
      "required_quantity": "<frequency × duration>",
      "Availability": "<Yes or No, based on internal database>"
    }
  ]
}
Instructions:
- All values must be extracted directly from the handwritten image — do not invent or assume any values.
- Compute `required_quantity` by multiplying the extracted frequency and duration.
- Check Availability using the pharmacy inventory database and return either "Yes" or "No".
- Do NOT include dosage or price.
- Do NOT include any extra explanation, markdown formatting, or code blocks. Return only plain, valid JSON.
"""

last_parsed_json = {}

def sell_and_update(drug_name: str, qty: int):
    try:
        drug_id = get_drug_id(drug_name)
        stock = get_available_stock(drug_id)
        if stock >= qty:
            insert_sale(drug_id, qty)
            update_stock(drug_id, qty)
            new_stock = get_available_stock(drug_id)
            status = f"✅ Sale recorded for {drug_name} ({qty} units)\n📦 Remaining stock: {new_stock} units"
        else:
            return None, gr.update(), f"❌ Not enough stock for {drug_name} (Available: {stock})", []

        updated_table_data = []
        sell_options = []

        for med in last_parsed_json.get("medicines", []):
            name = med.get("name", "N/A").strip()
            freq = med.get("frequency", "0")
            duration = med.get("duration", "0")
            required_qty = int(med.get("required_quantity", "0"))
            try:
                drug_id = get_drug_id(name)
                stock = get_available_stock(drug_id)
                is_avail = stock >= required_qty
                avail = "Yes" if is_avail else "No"
            except:
                avail = "No"

            updated_table_data.append([name, freq, duration, required_qty, "✅" if avail == "Yes" else "❌"])

            if avail == "Yes" and name and required_qty > 0:
                sell_options.append((f"{name} ({required_qty})", f"{name}|||{required_qty}"))

        full_inventory = get_full_inventory()
        return updated_table_data, gr.update(choices=sell_options), status, full_inventory

    except Exception as e:
        print("[ERROR in sell_and_update]:", e)
        return None, gr.update(), f"❌ Error processing sale for {drug_name}", []

def process_prescription(image: Image.Image):
    global last_parsed_json
    try:
        response = vision_model.generate_content([vision_prompt, image])
        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE)

        parsed_json = json.loads(raw_text)
        last_parsed_json = parsed_json
        run_agent(parsed_json)

        table_data = []
        sell_options = []

        for med in parsed_json.get("medicines", []):
            name = med.get("name", "N/A").strip()
            freq = med.get("frequency", "0")
            duration = med.get("duration", "0")
            qty = int(med.get("required_quantity", "0"))
            avail = med.get("Availability", "No")
            is_avail = str(avail).lower() == "yes"

            table_data.append([name, freq, duration, qty, "✅" if is_avail else "❌"])

            if is_avail and name and qty > 0:
                sell_options.append((f"{name} ({qty})", f"{name}|||{qty}"))

        full_inventory = get_full_inventory()
        return table_data, gr.update(choices=sell_options, value=None), "", full_inventory

    except Exception as e:
        import traceback
        print("[ERROR]:", e)
        traceback.print_exc()
        return [["Error", "", "", "", str(e)]], gr.update(choices=[]), f"❌ Failed to process image.", []

def sell_from_dropdown(selection):
    if not selection:
        return None, gr.update(), "❌ No drug selected.", []
    try:
        if "|||" in selection:
            name, qty = selection.split("|||")
            return sell_and_update(name.strip(), int(qty))
        else:
            return None, gr.update(), "❌ Malformed selection. Please reprocess prescription.", []
    except Exception as e:
        print("[ERROR in sell_from_dropdown]:", e)
        return None, gr.update(), f"❌ Failed to process selection ({selection}): {e}", []

def reset_app():
    return (
        gr.update(value=None),         # Clear image
        [],                            # Empty table
        gr.update(choices=[], value=None),  # Clear dropdown
        "",                            # Clear status
        get_full_inventory()           # Refresh inventory
    )

with gr.Blocks(css=".gr-button { font-weight: bold; }") as app:
    gr.Markdown("## PharmAssist 🏥💊")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("#### Upload Prescription")
            image_input = gr.Image(
                type="pil",
                label=None,
                height=200,
                width=250,
                show_download_button=True
            )
            process_button = gr.Button("🔍 Upload & Process", variant="primary")

    gr.Markdown("---")

    gr.Markdown("### 📋 Prescription Details")
    table = gr.Dataframe(
        headers=["Drug Name", "Frequency / Day", "Duration (Days)", "Required Quantity", "Available"],
        interactive=False,
        wrap=True,
        row_count=5
    )

    gr.Markdown("### 🧑‍⚕️ Pharmacist Actions")
    with gr.Row():
        sell_dropdown = gr.Dropdown(
            label="Select Drug to Sell",
            choices=[],
            interactive=True,
            allow_custom_value=False
        )
        sell_button = gr.Button("💊 Sell Selected Drug", variant="secondary")
        reset_button = gr.Button("🔁 Reset App", variant="secondary")

    status_box = gr.Textbox(label="Status", interactive=False, lines=2)

    gr.Markdown("### 🧾 Complete Inventory")
    inventory_table = gr.Dataframe(
        headers=["Drug Name", "Brand", "Quantity Left", "Expiry Date", "Price / Unit"],
        interactive=False,
        row_count=10
    )

    # Button actions
    process_button.click(
        fn=process_prescription,
        inputs=image_input,
        outputs=[table, sell_dropdown, status_box, inventory_table]
    )

    sell_button.click(
        fn=sell_from_dropdown,
        inputs=sell_dropdown,
        outputs=[table, sell_dropdown, status_box, inventory_table]
    )

    reset_button.click(
        fn=reset_app,
        inputs=[],
        outputs=[image_input, table, sell_dropdown, status_box, inventory_table]
    )

if __name__ == "__main__":
    app.launch(share=True)
