from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database import db, AuditLog, Appeal
from signals import get_groq_score, get_stylometric_score, get_vocabulary_richness
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///provenance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"],
    storage_uri="memory://",
)

@app.route('/submit', methods=['POST'])
@limiter.limit("10 per minute")
def submit():
    data = request.json
    if not data or 'text' not in data or 'creator_id' not in data:
        return jsonify({"error": "Missing text or creator_id"}), 400

    text = data['text']
    creator_id = data['creator_id']

    s1 = get_groq_score(text)
    s2 = get_stylometric_score(text)
    s3 = get_vocabulary_richness(text)
    
    final_score = (s1 * 0.5) + (s2 * 0.25) + (s3 * 0.25)
    
    if final_score >= 0.8:
        attribution = "likely_ai"
        label = "This content has been identified as AI-generated with high certainty. It likely lacks original human authorship."
    elif final_score <= 0.4:
        attribution = "likely_human"
        label = "This content has been verified as human-authored with high confidence. It shows strong markers of original creative work."
    else:
        attribution = "uncertain"
        label = "The origin of this content is unclear. Our analysis detected a mix of signals that suggest it may contain AI-generated elements or heavy AI assistance."

    new_log = AuditLog(
        creator_id=creator_id,
        attribution=attribution,
        confidence=final_score,
        llm_score=s1,
        signals=f"groq={s1:.4f}; stylometric={s2:.4f}; vocabulary={s3:.4f}",
        status="classified"
    )
    db.session.add(new_log)
    db.session.commit()

    return jsonify({
        "content_id": new_log.content_id,
        "attribution": attribution,
        "confidence": round(final_score, 2),
        "label": label
    })

@app.route('/appeal', methods=['POST'])
def appeal():
    data = request.json
    sub_id = data.get('content_id')
    reason = data.get('creator_reasoning')
    
    log = AuditLog.query.get(sub_id)
    if log:
        log.status = "under_review"
        new_appeal = Appeal(submission_id=sub_id, reason=reason)
        db.session.add(new_appeal)
        db.session.commit()
        return jsonify({"message": "Appeal received", "status": "under_review"}), 200
    return jsonify({"error": "Submission ID not found"}), 404

@app.route('/log', methods=['GET'])
def get_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    return jsonify({"entries": [log.to_dict() for log in logs]})

@app.route('/analytics', methods=['GET'])
def analytics():
    total = AuditLog.query.count()
    if total == 0: return jsonify({"total_submissions": 0})
    ai_count = AuditLog.query.filter_by(attribution="likely_ai").count()
    appeals_count = Appeal.query.count()
    return jsonify({
        "total_submissions": total,
        "ai_percentage": round((ai_count / total * 100), 2),
        "total_appeals": appeals_count,
        "appeal_rate": round((appeals_count / total * 100), 2)
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
