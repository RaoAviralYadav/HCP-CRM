import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { updateFormData } from '../store/interactionSlice'

const INTERACTION_TYPES = ['Meeting', 'Call', 'Email', 'Conference', 'Virtual Meeting', 'Workshop']
const SENTIMENTS = ['Positive', 'Neutral', 'Negative']

export default function InteractionForm() {
  const dispatch = useDispatch()
  const { formData, isSaving, lastSaved } = useSelector(s => s.interaction)

  const update = (field, value) => dispatch(updateFormData({ [field]: value }))

  const isEmpty = !formData.hcp_name && !formData.topics_discussed

  return (
    <div className="form-panel">
      <div className="panel-header">
        <h2 className="panel-title">Log HCP Interaction</h2>
        {lastSaved && (
          <span className="saved-badge">✓ Saved</span>
        )}
      </div>

      <div className="form-scroll">
        {isEmpty && (
          <div className="empty-hint">
            <div className="empty-hint-icon">💬</div>
            <p>Use the <strong>AI Assistant</strong> on the right to fill this form.<br />
            Describe your interaction in natural language.</p>
          </div>
        )}

        <section className="form-section">
          <h3 className="section-title">Interaction Details</h3>

          <div className="form-row">
            <div className="form-group">
              <label>HCP Name</label>
              <input
                type="text"
                placeholder="Search or select HCP..."
                value={formData.hcp_name}
                onChange={e => update('hcp_name', e.target.value)}
                className={formData.hcp_name ? 'filled' : ''}
              />
            </div>
            <div className="form-group">
              <label>Interaction Type</label>
              <select
                value={formData.interaction_type}
                onChange={e => update('interaction_type', e.target.value)}
                className={formData.interaction_type !== 'Meeting' ? 'filled' : ''}
              >
                {INTERACTION_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Date</label>
              <input
                type="date"
                value={formData.date}
                onChange={e => update('date', e.target.value)}
                className={formData.date ? 'filled' : ''}
              />
            </div>
            <div className="form-group">
              <label>Time</label>
              <input
                type="time"
                value={formData.time}
                onChange={e => update('time', e.target.value)}
                className={formData.time ? 'filled' : ''}
              />
            </div>
          </div>

          <div className="form-group full">
            <label>Attendees</label>
            <input
              type="text"
              placeholder="Enter names or search..."
              value={formData.attendees}
              onChange={e => update('attendees', e.target.value)}
              className={formData.attendees ? 'filled' : ''}
            />
          </div>

          <div className="form-group full">
            <label>Topics Discussed</label>
            <textarea
              rows={3}
              placeholder="Enter key discussion points..."
              value={formData.topics_discussed}
              onChange={e => update('topics_discussed', e.target.value)}
              className={formData.topics_discussed ? 'filled' : ''}
            />
          </div>
        </section>

        <section className="form-section">
          <h3 className="section-title">Materials & Samples</h3>

          <div className="form-group full">
            <label>Materials Shared</label>
            <div className="tag-area">
              {formData.materials_shared?.length > 0 ? (
                formData.materials_shared.map((m, i) => (
                  <span key={i} className="tag tag-blue">{m}</span>
                ))
              ) : (
                <span className="tag-placeholder">No materials added</span>
              )}
            </div>
          </div>

          <div className="form-group full">
            <label>Samples Distributed</label>
            <div className="tag-area">
              {formData.samples_distributed?.length > 0 ? (
                formData.samples_distributed.map((s, i) => (
                  <span key={i} className="tag tag-green">{s}</span>
                ))
              ) : (
                <span className="tag-placeholder">No samples added</span>
              )}
            </div>
          </div>
        </section>

        <section className="form-section">
          <h3 className="section-title">Observed / Inferred HCP Sentiment</h3>
          <div className="sentiment-group">
            {SENTIMENTS.map(s => (
              <label key={s} className={`sentiment-option sentiment-${s.toLowerCase()} ${formData.sentiment === s ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="sentiment"
                  value={s}
                  checked={formData.sentiment === s}
                  onChange={() => update('sentiment', s)}
                />
                <span className="sentiment-dot"></span>
                {s}
              </label>
            ))}
          </div>
        </section>

        <section className="form-section">
          <div className="form-group full">
            <label>Outcomes</label>
            <textarea
              rows={3}
              placeholder="Key outcomes or agreements..."
              value={formData.outcomes}
              onChange={e => update('outcomes', e.target.value)}
              className={formData.outcomes ? 'filled' : ''}
            />
          </div>

          <div className="form-group full">
            <label>Follow-up Actions</label>
            <textarea
              rows={2}
              placeholder="Enter next steps or tasks..."
              value={formData.follow_up_actions}
              onChange={e => update('follow_up_actions', e.target.value)}
              className={formData.follow_up_actions ? 'filled' : ''}
            />
          </div>
        </section>

        {formData.ai_suggested_followups?.length > 0 && (
          <section className="form-section ai-suggestions">
            <h3 className="section-title ai-title">
              <span className="ai-badge">✦ AI</span>
              Suggested Follow-ups
            </h3>
            <ul className="suggestion-list">
              {formData.ai_suggested_followups.map((s, i) => (
                <li key={i} className="suggestion-item">
                  <span className="suggestion-arrow">→</span> {s}
                </li>
              ))}
            </ul>
          </section>
        )}

        {formData.id && (
          <div className="record-id">
            Interaction ID: <strong>#{formData.id}</strong>
          </div>
        )}
      </div>
    </div>
  )
}