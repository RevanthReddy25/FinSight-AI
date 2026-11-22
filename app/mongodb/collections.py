from app.mongodb.connection import mongodb


invoice_collection = mongodb["invoice_extractions"]

processing_logs_collection = mongodb["ai_processing_logs"]

document_metadata_collection = mongodb["document_metadata"]