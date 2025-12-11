import pandas as pd
import numpy as np
import os
import sys
from io import StringIO
from typing import Dict, Any, List, Optional
from scipy import stats
from AgentPandas.message_broker import message_broker


async def ask_compliance_agent(question: str) -> Dict[str, Any]:
    """
    Asks the Compliance Agent to validate an expense or spending pattern against company policy.
    Uses JSON message passing for inter-agent communication.

    Args:
        question: Natural language question about compliance (e.g., "Is it ok spending $10,000 on barbed wire?")

    Returns:
        Dict with compliance response including whether the expense is allowed

    Example:
        result = await ask_compliance_agent("Does the policy allow spending $400 in category 'Other'?")
    """
    try:
        # Send JSON message to Compliance Agent
        response = await message_broker.send_message(
            from_agent="FRAUD_DETECTOR",
            to_agent="COMPLIANCE",
            message_type="COMPLIANCE_CHECK",
            payload={"question": question},
        )

        if response["status"] == "SUCCESS":
            return {
                "success": True,
                "question": question,
                "compliance_response": response["response"]["compliance_response"],
                "is_violation": response["response"]["is_violation"],
            }
        else:
            return {
                "success": False,
                "question": question,
                "error": response.get("error", "Unknown error"),
            }
    except Exception as e:
        return {
            "success": False,
            "question": question,
            "error": f"Failed to contact compliance agent: {str(e)}",
        }


async def send_email_notification(
    recipient: str, subject: str, message: str
) -> Dict[str, Any]:
    """
    Sends an email notification via the Email Agent to notify about suspicious transactions or request clarification.
    Uses JSON message passing for inter-agent communication.

    Args:
        recipient: Employee name or email to send to (e.g., "Jim Halpert")
        subject: Email subject line
        message: Email body content

    Returns:
        Dict with success status and email details

    Example:
        result = await send_email_notification(
            recipient="Jim Halpert",
            subject="Clarification Needed: Large Purchase",
            message="We noticed a $10,000 purchase on barbed wire. Can you provide more details?"
        )
    """
    try:
        # Send JSON message to Email Agent
        response = await message_broker.send_message(
            from_agent="FRAUD_DETECTOR",
            to_agent="EMAIL",
            message_type="SEND_EMAIL",
            payload={"recipient": recipient, "subject": subject, "body": message},
        )

        if response["status"] == "SUCCESS":
            return {
                "success": True,
                "recipient": recipient,
                "subject": subject,
                "message": message,
                "result": response["response"]["result"],
            }
        else:
            return {
                "success": False,
                "recipient": recipient,
                "error": response.get("error", "Unknown error"),
            }
    except Exception as e:
        return {
            "success": False,
            "recipient": recipient,
            "error": f"Failed to send email: {str(e)}",
        }


async def request_orchestrator_data(data_request: str) -> Dict[str, Any]:
    """
    Requests additional data or analysis from the Orchestrator agent.
    Uses JSON message passing for inter-agent communication.

    Args:
        data_request: Description of what data is needed (e.g., "Get employee purchase history for Jim Halpert")

    Returns:
        Dict with requested data

    Example:
        result = await request_orchestrator_data("Get all transactions for employee Angela Martin in 2024")
    """
    try:
        # Send JSON message to Orchestrator
        response = await message_broker.send_message(
            from_agent="FRAUD_DETECTOR",
            to_agent="ORCHESTRATOR",
            message_type="DATA_REQUEST",
            payload={"data_request": data_request},
        )

        if response["status"] == "SUCCESS":
            return {
                "success": True,
                "request": data_request,
                "data": response["response"]["data"],
            }
        else:
            return {
                "success": False,
                "request": data_request,
                "error": response.get("error", "Unknown error"),
            }
    except Exception as e:
        return {
            "success": False,
            "request": data_request,
            "error": f"Failed to contact orchestrator: {str(e)}",
        }


async def ask_compliance_agent(question: str) -> Dict[str, Any]:
    """
    Asks the Compliance Agent to validate an expense or spending pattern against company policy.

    Args:
        question: Natural language question about compliance (e.g., "Is it ok spending $10,000 on barbed wire?")

    Returns:
        Dict with compliance response including whether the expense is allowed

    Example:
        result = await ask_compliance_agent("Does the policy allow spending $400 in category 'Other'?")
    """
    try:
        # Import the compliance agent
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from agentCompliance.agent import run_agent as run_compliance_agent

        response, success = await run_compliance_agent(question)

        return {
            "success": success,
            "question": question,
            "compliance_response": response,
            "is_violation": "not allowed" in response.lower()
            or "does not allow" in response.lower()
            or "não permite" in response.lower(),
        }
    except Exception as e:
        return {
            "success": False,
            "question": question,
            "error": f"Failed to contact compliance agent: {str(e)}",
        }


async def send_email_notification(
    recipient: str, subject: str, message: str
) -> Dict[str, Any]:
    """
    Sends an email notification via the Email Agent to notify about suspicious transactions or request clarification.

    Args:
        recipient: Employee name or email to send to (e.g., "Jim Halpert")
        subject: Email subject line
        message: Email body content

    Returns:
        Dict with success status and email details

    Example:
        result = await send_email_notification(
            recipient="Jim Halpert",
            subject="Clarification Needed: Large Purchase",
            message="We noticed a $10,000 purchase on barbed wire. Can you provide more details?"
        )
    """
    try:
        # Import the email agent
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from agentEmail.agent import send_email

        result = await send_email(recipient=recipient, subject=subject, body=message)

        return {
            "success": True,
            "recipient": recipient,
            "subject": subject,
            "message": message,
            "result": result,
        }
    except Exception as e:
        return {
            "success": False,
            "recipient": recipient,
            "error": f"Failed to send email: {str(e)}",
        }


async def request_orchestrator_data(data_request: str) -> Dict[str, Any]:
    """
    Requests additional data or analysis from the Orchestrator agent.

    Args:
        data_request: Description of what data is needed (e.g., "Get employee purchase history for Jim Halpert")

    Returns:
        Dict with requested data

    Example:
        result = await request_orchestrator_data("Get all transactions for employee Angela Martin in 2024")
    """
    try:
        # Import the orchestrator
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from orchestrator.agent import handle_request

        result = await handle_request(data_request)

        return {"success": True, "request": data_request, "data": result}
    except Exception as e:
        return {
            "success": False,
            "request": data_request,
            "error": f"Failed to contact orchestrator: {str(e)}",
        }


def download_csv_from_bucket(
    bucket_name: str = "", blob_name: str = "", cache_dir: str = "./cache"
) -> Dict[str, Any]:
    """
    Downloads CSV from Google Cloud Storage using HMAC credentials.

    Args:
        bucket_name: Ignored - kept for compatibility
        blob_name: Ignored - kept for compatibility
        cache_dir: Local directory to cache downloaded files

    Returns:
        Dict with success status, local_path, metadata, or error message
    """
    # Hardcoded credentials and file info
    ACCESS_KEY = os.environ['ACCESS_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    BUCKET_NAME = os.environ['BUCKET_NAME']
    BLOB_NAME = os.environ['BLOB_NAME']

    try:
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Generate local filename
        local_path = os.path.join(cache_dir, "transacoes_bancarias.csv")

        print(f"Downloading gs://{BUCKET_NAME}/{BLOB_NAME}...")

        # Use boto3 for S3-compatible access with HMAC
        try:
            import boto3
            from botocore.client import Config

            # Create S3 client configured for Google Cloud Storage
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                endpoint_url="https://storage.googleapis.com",
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )

            # Download the file
            s3_client.download_file(BUCKET_NAME, BLOB_NAME, local_path)

            # Get metadata
            response = s3_client.head_object(Bucket=BUCKET_NAME, Key=BLOB_NAME)
            metadata = {
                "bucket": BUCKET_NAME,
                "blob": BLOB_NAME,
                "size_bytes": response.get("ContentLength", 0),
                "content_type": response.get("ContentType", "text/csv"),
            }

        except ImportError:
            # Fallback: use requests with manual HMAC signing
            import requests
            import hmac
            import hashlib
            import base64
            from email.utils import formatdate

            url = f"https://storage.googleapis.com/{BUCKET_NAME}/{BLOB_NAME}"
            date_str = formatdate(timeval=None, localtime=False, usegmt=True)

            # Create string to sign (AWS S3 v2 signature style)
            string_to_sign = f"GET\n\n\n{date_str}\n/{BUCKET_NAME}/{BLOB_NAME}"

            # Sign with HMAC-SHA1 (not SHA256 - GCS uses SHA1 like AWS S3 v2)
            signature = base64.b64encode(
                hmac.new(
                    SECRET_KEY.encode("utf-8"),
                    string_to_sign.encode("utf-8"),
                    hashlib.sha1,
                ).digest()
            ).decode("utf-8")

            # Make request with authorization
            headers = {
                "Date": date_str,
                "Authorization": f"GOOG1 {ACCESS_KEY}:{signature}",
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

            metadata = {
                "bucket": BUCKET_NAME,
                "blob": BLOB_NAME,
                "size_bytes": len(response.content),
                "content_type": response.headers.get("content-type", "text/csv"),
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

            metadata = {
                "bucket": BUCKET_NAME,
                "blob": BLOB_NAME,
                "size_bytes": len(response.content),
                "content_type": response.headers.get("content-type", "text/csv"),
            }

        print(f"✅ Downloaded to {local_path}")
        return {"success": True, "local_path": local_path, "metadata": metadata}

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to download file: {str(e)}",
            "local_path": None,
            "metadata": {},
        }


def load_csv_preview(local_path: str, rows: int = 5) -> Dict[str, Any]:
    """
    Loads a CSV file and returns basic information plus preview.

    Args:
        local_path: Path to the local CSV file
        rows: Number of rows to preview (default: 5)

    Returns:
        Dict with columns, shape, dtypes, preview, and sample rows
    """
    try:
        # Load the CSV
        df = pd.read_csv(local_path)

        # Get column information
        columns = df.columns.tolist()
        shape = df.shape
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

        # Create preview string
        preview_df = df.head(rows)
        preview_str = preview_df.to_string()

        # Convert preview to list of dicts for structured access
        sample_rows = preview_df.to_dict(orient="records")

        # Memory usage
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

        return {
            "success": True,
            "columns": columns,
            "shape": shape,  # (rows, columns)
            "dtypes": dtypes,
            "preview": preview_str,
            "sample_rows": sample_rows,
            "memory_mb": round(memory_mb, 2),
            "null_counts": df.isnull().sum().to_dict(),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to load CSV: {str(e)}"}


def get_statistics(local_path: str, column: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns statistical summary of the dataset.

    Args:
        local_path: Path to the local CSV file
        column: Specific column to analyze (optional, analyzes all if None)

    Returns:
        Dict with numeric and categorical summaries
    """
    try:
        df = pd.read_csv(local_path)

        result = {
            "success": True,
            "total_rows": len(df),
            "total_columns": len(df.columns),
        }

        # If specific column requested
        if column:
            if column not in df.columns:
                return {
                    "success": False,
                    "error": f"Column '{column}' not found in dataset",
                }

            col_data = df[column]

            if pd.api.types.is_numeric_dtype(col_data):
                result["column_stats"] = {
                    "name": column,
                    "type": "numeric",
                    "count": int(col_data.count()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q25": float(col_data.quantile(0.25)),
                    "q75": float(col_data.quantile(0.75)),
                }
            else:
                result["column_stats"] = {
                    "name": column,
                    "type": "categorical",
                    "count": int(col_data.count()),
                    "unique_values": int(col_data.nunique()),
                    "top_value": str(col_data.mode()[0])
                    if len(col_data.mode()) > 0
                    else None,
                    "top_frequency": int(col_data.value_counts().iloc[0])
                    if len(col_data) > 0
                    else 0,
                    "value_counts": col_data.value_counts().head(10).to_dict(),
                }
        else:
            # Analyze all columns
            numeric_summary = {}
            categorical_summary = {}

            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    numeric_summary[col] = {
                        "mean": float(df[col].mean())
                        if not df[col].isna().all()
                        else None,
                        "median": float(df[col].median())
                        if not df[col].isna().all()
                        else None,
                        "std": float(df[col].std())
                        if not df[col].isna().all()
                        else None,
                        "min": float(df[col].min())
                        if not df[col].isna().all()
                        else None,
                        "max": float(df[col].max())
                        if not df[col].isna().all()
                        else None,
                        "q25": float(df[col].quantile(0.25))
                        if not df[col].isna().all()
                        else None,
                        "q75": float(df[col].quantile(0.75))
                        if not df[col].isna().all()
                        else None,
                    }
                else:
                    categorical_summary[col] = {
                        "unique_values": int(df[col].nunique()),
                        "top_value": str(df[col].mode()[0])
                        if len(df[col].mode()) > 0
                        else None,
                        "top_frequency": int(df[col].value_counts().iloc[0])
                        if len(df[col]) > 0
                        else 0,
                    }

            result["numeric_summary"] = numeric_summary
            result["categorical_summary"] = categorical_summary
            result["missing_values"] = df.isnull().sum().to_dict()

        return result

    except Exception as e:
        return {"success": False, "error": f"Failed to compute statistics: {str(e)}"}


def execute_pandas_code(local_path: str, code: str) -> Dict[str, Any]:
    """
    Executes arbitrary pandas code on the DataFrame with security restrictions.

    Args:
        local_path: Path to the local CSV file
        code: Python/pandas code to execute (has access to 'df' variable)

    Returns:
        Dict with execution result, output, or error
    """
    # Security: Block dangerous patterns
    BLOCKED_PATTERNS = [
        "import ",
        "from ",
        "open(",
        "exec(",
        "eval(",
        "__",
        "compile(",
        "globals(",
        "locals(",
        "vars(",
        "dir(",
        "file",
        "os.",
        "sys.",
        "subprocess",
        "pickle",
        "marshal",
        "shelve",
        "socket",
        "requests",
        "urllib",
        "write",
        "delete",
        "remove",
        "unlink",
        "rmdir",
    ]

    for pattern in BLOCKED_PATTERNS:
        if pattern in code.lower():
            return {
                "success": False,
                "error": f"Security violation: Code contains blocked pattern '{pattern}'",
            }

    try:
        # Load the CSV
        df = pd.read_csv(local_path)

        # Create a restricted namespace
        namespace = {
            "df": df,
            "pd": pd,
            "np": np,
            "__builtins__": {
                "len": len,
                "max": max,
                "min": min,
                "sum": sum,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "range": range,
                "list": list,
                "dict": dict,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "True": True,
                "False": False,
                "None": None,
                "print": print,
            },
        }

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            # Try to execute as expression first (returns value)
            result = eval(code, namespace)
            result_str = str(result)

            # Limit output size
            if len(result_str) > 5000:
                result_str = result_str[:5000] + "\n... (output truncated)"

        except SyntaxError:
            # If not an expression, try as statements
            exec(code, namespace)
            result_str = "Code executed successfully (no return value)"

        # Restore stdout
        sys.stdout = old_stdout
        output = captured_output.getvalue()

        return {
            "success": True,
            "result": result_str,
            "output": output if output else None,
        }

    except Exception as e:
        sys.stdout = old_stdout
        return {"success": False, "error": f"Execution error: {str(e)}"}


def detect_fraud_patterns(local_path: str) -> Dict[str, Any]:
    """
    Runs predefined fraud detection checks on the CSV.

    Args:
        local_path: Path to the local CSV file

    Returns:
        Dict with detected fraud patterns categorized by type
    """
    try:
        df = pd.read_csv(local_path)

        results = {"success": True, "total_transactions": len(df), "fraud_patterns": {}}

        # Pattern 1: Duplicate Transactions
        # Look for duplicates based on key fields (adjust column names as needed)
        duplicate_cols = []
        for cols in [
            ["employee_id", "date", "amount", "vendor"],
            ["date", "amount", "vendor"],
            ["amount", "vendor"],
        ]:
            if all(col in df.columns for col in cols):
                duplicate_cols = cols
                break

        if duplicate_cols:
            duplicates = df[df.duplicated(subset=duplicate_cols, keep=False)]
            if len(duplicates) > 0:
                results["fraud_patterns"]["duplicates"] = {
                    "count": len(duplicates),
                    "severity": "HIGH",
                    "description": f"Found {len(duplicates)} duplicate transactions",
                    "sample": duplicates.head(5).to_dict(orient="records"),
                }

        # Pattern 2: Threshold Splitting (assuming $500 limit)
        if "amount" in df.columns:
            threshold = 500
            near_threshold = df[
                (df["amount"] >= threshold * 0.95) & (df["amount"] < threshold)
            ]

            if len(near_threshold) > 5:  # Multiple transactions near threshold
                results["fraud_patterns"]["threshold_splitting"] = {
                    "count": len(near_threshold),
                    "severity": "HIGH",
                    "description": f"Found {len(near_threshold)} transactions between ${threshold * 0.95:.2f} and ${threshold}",
                    "sample": near_threshold.head(5).to_dict(orient="records"),
                }

            # Pattern 3: Round Number Bias
            round_numbers = df[df["amount"] % 100 == 0]
            if len(round_numbers) > len(df) * 0.15:  # More than 15% are round numbers
                results["fraud_patterns"]["round_numbers"] = {
                    "count": len(round_numbers),
                    "severity": "MEDIUM",
                    "description": f"Found {len(round_numbers)} transactions with round amounts (suspicious pattern)",
                    "sample": round_numbers.head(5).to_dict(orient="records"),
                }

            # Pattern 4: Statistical Outliers
            if len(df) > 10:
                z_scores = np.abs(stats.zscore(df["amount"].dropna()))
                outliers_mask = z_scores > 3
                outliers = df[df["amount"].notna()].iloc[np.where(outliers_mask)[0]]

                if len(outliers) > 0:
                    results["fraud_patterns"]["outliers"] = {
                        "count": len(outliers),
                        "severity": "MEDIUM",
                        "description": f"Found {len(outliers)} statistical outliers (>3 std deviations)",
                        "sample": outliers.head(5).to_dict(orient="records"),
                    }

        # Pattern 5: Weekend/Holiday Transactions
        if "date" in df.columns:
            try:
                df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
                weekend_txns = df[df["date_parsed"].dt.dayofweek >= 5]

                if len(weekend_txns) > 0:
                    results["fraud_patterns"]["weekend_transactions"] = {
                        "count": len(weekend_txns),
                        "severity": "LOW",
                        "description": f"Found {len(weekend_txns)} weekend transactions",
                        "sample": weekend_txns.head(5).to_dict(orient="records"),
                    }
            except:
                pass  # Skip if date parsing fails

        # Pattern 6: High-Frequency Employees
        if "employee_id" in df.columns:
            txn_counts = df["employee_id"].value_counts()
            median_count = txn_counts.median()
            high_freq = txn_counts[txn_counts > median_count * 2.5]

            if len(high_freq) > 0:
                results["fraud_patterns"]["high_frequency"] = {
                    "count": len(high_freq),
                    "severity": "MEDIUM",
                    "description": f"Found {len(high_freq)} employees with unusually high transaction frequency",
                    "employees": high_freq.to_dict(),
                }

        # Pattern 7: Suspicious Vendors
        if "vendor" in df.columns:
            vendors = df["vendor"].value_counts()
            single_use_vendors = vendors[vendors == 1]

            # Look for suspicious keywords
            suspicious_keywords = [
                "cash",
                "personal",
                "misc",
                "other",
                "reimburse",
                "llc",
            ]
            suspicious_vendors = df[
                df["vendor"]
                .str.lower()
                .str.contains("|".join(suspicious_keywords), na=False)
            ]

            if len(suspicious_vendors) > 0:
                results["fraud_patterns"]["suspicious_vendors"] = {
                    "count": len(suspicious_vendors),
                    "severity": "MEDIUM",
                    "description": f"Found {len(suspicious_vendors)} transactions with suspicious vendor names",
                    "sample": suspicious_vendors.head(5).to_dict(orient="records"),
                }

        return results

    except Exception as e:
        return {"success": False, "error": f"Failed to detect fraud patterns: {str(e)}"}
