import json
import base64
import boto3
import os

textract = boto3.client("textract")

def _parse_event(event):
    """
    Function URL / API Gateway se aane wale event ko normalize karta hai.
    Expecting: body JSON with keys: resume_json, doc_base64
    """
    if isinstance(event, dict) and "body" in event:
        body = event["body"]
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {}
    else:
        data = event if isinstance(event, dict) else {}

    return {
        "resume_json": data.get("resume_json", {}),
        "doc_base64": data.get("doc_base64", ""),
    }


def lambda_handler(event, context):
    try:
        parsed = _parse_event(event)
        resume = parsed["resume_json"]
        doc_b64 = parsed["doc_base64"]

        if not resume or not doc_b64:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "resume_json and doc_base64 are required"})
            }

        # ---- Textract call ----
        img_bytes = base64.b64decode(doc_b64)

        response = textract.analyze_document(
            Document={"Bytes": img_bytes},
            FeatureTypes=["FORMS"]
        )

        words = [
            block["Text"]
            for block in response["Blocks"]
            if block["BlockType"] == "WORD"
        ]
        full_text = " ".join(words)

        name = str(resume.get("Name", "")).strip()
        email = str(resume.get("Email", "")).strip()

        # simple lowercase contains check
        name_found = name.split()[0].lower() in full_text.lower() if name else False
        email_user = email.split("@")[0].lower() if "@" in email else email.lower()
        email_found = email_user in full_text.lower() if email_user else False

        match_score = (int(name_found) + int(email_found)) / 2 * 100 if (name or email) else 0

        result = {
            "name_in_resume": name,
            "email_in_resume": email,
            "name_found_in_doc": name_found,
            "email_found_in_doc": email_found,
            "match_score": match_score,
            "matched": match_score >= 50,
            "text_snippet": full_text[:300]
        }

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
