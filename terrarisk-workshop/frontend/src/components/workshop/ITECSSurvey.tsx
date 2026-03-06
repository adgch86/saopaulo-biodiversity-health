'use client';

import { useState, useEffect } from 'react';
import { useWorkshopStore } from '@/lib/store';
import type { ITECSResponses, ITECSCollaborator } from '@/lib/types';

// ─── Likert scale 1-7 ────────────────────────────────────────────────────────

function LikertScale({
  value,
  onChange,
  disabled,
}: {
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
}) {
  return (
    <div className="flex items-center gap-1 mt-2">
      <span className="text-xs text-gray-400 w-24 text-right shrink-0">Discordo totalmente</span>
      <div className="flex gap-1 mx-2">
        {[1, 2, 3, 4, 5, 6, 7].map((n) => (
          <button
            key={n}
            type="button"
            disabled={disabled}
            onClick={() => onChange(n)}
            className={`w-9 h-9 rounded-full text-sm font-semibold border-2 transition-all
              ${value === n
                ? 'bg-purple-600 border-purple-600 text-white scale-110'
                : 'border-gray-300 text-gray-500 hover:border-purple-400 hover:text-purple-600'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {n}
          </button>
        ))}
      </div>
      <span className="text-xs text-gray-400 w-24 shrink-0">Concordo totalmente</span>
    </div>
  );
}

// ─── Likert item ──────────────────────────────────────────────────────────────

function LikertItem({
  n,
  label,
  value,
  onChange,
  disabled,
}: {
  n: number;
  label: string;
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
}) {
  return (
    <div className={`py-3 border-b border-gray-100 last:border-0 ${value === 0 && !disabled ? 'bg-amber-50 rounded' : ''}`}>
      <div className="flex items-start gap-2">
        <span className="text-xs font-bold text-gray-400 mt-0.5 w-5 shrink-0">{n}.</span>
        <div className="flex-1">
          <p className="text-sm text-gray-700">{label}</p>
          <LikertScale value={value} onChange={onChange} disabled={disabled} />
        </div>
      </div>
    </div>
  );
}

// ─── Collaborator table ───────────────────────────────────────────────────────

const FREQ_OPTIONS: { value: ITECSCollaborator['frequency']; label: string }[] = [
  { value: 'more_than_monthly', label: 'Mais de uma vez por m\u00eas' },
  { value: 'monthly', label: 'Uma vez por m\u00eas' },
  { value: 'yearly', label: 'Uma vez por ano' },
  { value: 'sporadic', label: 'Espor\u00e1dica' },
];

function CollaboratorTable({
  value,
  onChange,
  disabled,
}: {
  value: ITECSCollaborator[];
  onChange: (v: ITECSCollaborator[]) => void;
  disabled: boolean;
}) {
  const updateRow = (idx: number, field: keyof ITECSCollaborator, val: string) => {
    const updated = value.map((row, i) =>
      i === idx ? { ...row, [field]: val } : row
    );
    onChange(updated);
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600 w-8">#</th>
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600">Pessoa / Institui&ccedil;&atilde;o / Rede</th>
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600">Tema de colabora&ccedil;&atilde;o</th>
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600">Frequ&ecirc;ncia</th>
          </tr>
        </thead>
        <tbody>
          {value.map((row, idx) => (
            <tr key={idx}>
              <td className="p-2 border border-gray-200 text-xs text-gray-400 text-center">{idx + 1}</td>
              <td className="p-1 border border-gray-200">
                <input
                  type="text"
                  disabled={disabled}
                  value={row.nameOrInstitution}
                  onChange={(e) => updateRow(idx, 'nameOrInstitution', e.target.value)}
                  placeholder="Nome ou institui&#231;&#227;o"
                  className="w-full px-2 py-1 text-sm rounded border-0 focus:ring-1 focus:ring-purple-400 disabled:bg-gray-50 disabled:text-gray-400"
                />
              </td>
              <td className="p-1 border border-gray-200">
                <input
                  type="text"
                  disabled={disabled}
                  value={row.topic}
                  onChange={(e) => updateRow(idx, 'topic', e.target.value)}
                  placeholder="Tema"
                  className="w-full px-2 py-1 text-sm rounded border-0 focus:ring-1 focus:ring-purple-400 disabled:bg-gray-50 disabled:text-gray-400"
                />
              </td>
              <td className="p-1 border border-gray-200">
                <select
                  disabled={disabled}
                  value={row.frequency}
                  onChange={(e) => updateRow(idx, 'frequency', e.target.value as ITECSCollaborator['frequency'])}
                  className="w-full px-2 py-1 text-sm rounded border-0 focus:ring-1 focus:ring-purple-400 disabled:bg-gray-50 disabled:text-gray-400"
                >
                  {FREQ_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Empty responses initializer ──────────────────────────────────────────────

function emptyResponses(): ITECSResponses {
  return {
    exp1: 0, exp2: 0, exp3: 0, exp4: 0,
    exp5: 0, exp6: 0, exp7: 0, exp8: 0,
    q9: '', q10: '', q11: '',
    q12: Array.from({ length: 5 }, () => ({ nameOrInstitution: '', topic: '', frequency: 'sporadic' as const })),
    q13: '',
    ps14: 0, ps15: 0,
    q16: false,
  };
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function ITECSSurvey() {
  const {
    group,
    surveySubmitted,
    setSurveySubmitted,
    surveyParticipantId,
    setSurveyParticipantId,
    setSurveyResponses,
    initialRanking,
    revisedRanking,
    selectedActions,
  } = useWorkshopStore();

  const [responses, setResponses] = useState<ITECSResponses>(emptyResponses());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!surveyParticipantId) {
      const id = crypto.randomUUID();
      setSurveyParticipantId(id);
    }
  }, [surveyParticipantId, setSurveyParticipantId]);

  const setLikert = (field: keyof ITECSResponses, value: number) => {
    setResponses((prev) => ({ ...prev, [field]: value }));
  };

  const missingLikert = (): string[] => {
    const likertFields: (keyof ITECSResponses)[] = [
      'exp1', 'exp2', 'exp3', 'exp4', 'exp5', 'exp6', 'exp7', 'exp8',
      'ps14', 'ps15',
    ];
    return likertFields.filter((f) => (responses[f] as number) === 0);
  };

  const handleSubmit = async () => {
    const missing = missingLikert();
    if (missing.length > 0) {
      setError(`Por favor, responda todos os itens de sele\u00e7\u00e3o (${missing.length} pendente${missing.length > 1 ? 's' : ''}).`);
      return;
    }
    if (!group) return;

    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`/api/workshop/survey`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          groupId: group.id,
          participantId: surveyParticipantId,
          responses,
          meta: {
            version: '2.0',
            layersPurchased: group.purchasedLayers ?? [],
            creditsSpent: Math.max(0, 10 - (group.credits ?? 10)),
            rankingChanged: initialRanking.length > 0 && revisedRanking.length > 0
              && JSON.stringify(initialRanking) !== JSON.stringify(revisedRanking),
            actionsSelected: selectedActions,
          },
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setSurveyResponses(responses);
      setSurveySubmitted(true);
    } catch (e) {
      setError('Erro ao enviar. Tente novamente.');
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  // ─── Submitted state ─────────────────────────────────────────────────────

  if (surveySubmitted) {
    return (
      <div className="flex-1 overflow-auto">
        <div className="max-w-2xl mx-auto p-8 text-center">
          <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Avalia&ccedil;&atilde;o enviada</h2>
          <p className="text-gray-600 mb-6">
            Obrigado pela sua participa&ccedil;&atilde;o. Suas respostas foram registradas e ser&atilde;o utilizadas
            para autoavalia&ccedil;&atilde;o e otimiza&ccedil;&atilde;o da ferramenta.
          </p>
          <div className="text-xs text-gray-400 italic">
            ITECS v2.0 &middot; TerraX &middot; Dados anonimizados
          </div>
        </div>
      </div>
    );
  }

  const disabled = submitting;

  // ─── Form ─────────────────────────────────────────────────────────────────

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      <div className="max-w-3xl mx-auto p-4 lg:p-8 space-y-8 pb-16">

        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl lg:text-2xl font-bold text-gray-800">Avalia&ccedil;&atilde;o TerraRisk</h1>
              <p className="text-xs text-gray-400">Instrumento de Avalia&ccedil;&atilde;o &middot; v2.0</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 bg-white rounded-lg p-4 border border-gray-200">
            Este instrumento avalia sua experi&ecirc;ncia com a ferramenta TerraRisk e o marco anal&iacute;tico TerraX.
            N&atilde;o h&aacute; respostas certas ou erradas. As respostas s&atilde;o utilizadas exclusivamente
            para fins de autoavalia&ccedil;&atilde;o e otimiza&ccedil;&atilde;o da ferramenta.
            S&atilde;o 10 perguntas de sele&ccedil;&atilde;o e 5 descritivas. O preenchimento leva aproximadamente 5 minutos.
          </p>
        </div>

        {/* Likert instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
          <strong>Escala:</strong> Para cada afirma&ccedil;&atilde;o, selecione de <strong>1</strong> (Discordo totalmente)
          a <strong>7</strong> (Concordo totalmente).
        </div>

        {/* ── BLOCO I — Experiência com o TerraRisk ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-4 p-4 rounded-lg bg-purple-50 border border-purple-200">
            <p className="text-xs font-semibold text-purple-500 uppercase tracking-wide">Bloco I &mdash; Experi&ecirc;ncia com o TerraRisk</p>
            <p className="text-sm text-purple-700 mt-1 font-medium">Como foi sua experi&ecirc;ncia com a ferramenta?</p>
          </div>
          <LikertItem n={1} label="A ferramenta me ajudou a entender melhor o territ\u00f3rio que analiso." value={responses.exp1} onChange={(v) => setLikert('exp1', v)} disabled={disabled} />
          <LikertItem n={2} label="Consigo identificar rela\u00e7\u00f5es entre vari\u00e1veis que antes n\u00e3o considerava." value={responses.exp2} onChange={(v) => setLikert('exp2', v)} disabled={disabled} />
          <LikertItem n={3} label="Os dados apresentados s\u00e3o relevantes para meu trabalho." value={responses.exp3} onChange={(v) => setLikert('exp3', v)} disabled={disabled} />
          <LikertItem n={4} label="A escala municipal foi adequada para a an\u00e1lise." value={responses.exp4} onChange={(v) => setLikert('exp4', v)} disabled={disabled} />
          <LikertItem n={5} label="Os resultados fazem sentido com o que conhe\u00e7o do territ\u00f3rio." value={responses.exp5} onChange={(v) => setLikert('exp5', v)} disabled={disabled} />
          <LikertItem n={6} label="A ferramenta \u00e9 \u00fatil para apoiar decis\u00f5es na minha \u00e1rea de atua\u00e7\u00e3o." value={responses.exp6} onChange={(v) => setLikert('exp6', v)} disabled={disabled} />
          <LikertItem n={7} label="Eu usaria o TerraRisk no meu trabalho." value={responses.exp7} onChange={(v) => setLikert('exp7', v)} disabled={disabled} />
          <LikertItem n={8} label="Recomendaria o TerraRisk a colegas ou institui\u00e7\u00f5es." value={responses.exp8} onChange={(v) => setLikert('exp8', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO II — Aplicação prática ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-4 p-4 rounded-lg bg-teal-50 border border-teal-200">
            <p className="text-xs font-semibold text-teal-600 uppercase tracking-wide">Bloco II &mdash; Aplica&ccedil;&atilde;o pr&aacute;tica</p>
            <p className="text-sm text-teal-700 mt-1 font-medium">Como voc&ecirc; aplicaria o TerraRisk?</p>
          </div>
          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">9.</span> Que problema concreto do seu trabalho o TerraRisk poderia ajudar a resolver?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q9}
                onChange={(e) => setResponses((p) => ({ ...p, q9: e.target.value }))}
                rows={3}
                placeholder="Descreva um problema concreto..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">10.</span> Que hip&oacute;tese causal espec&iacute;fica voc&ecirc; investigaria utilizando o TerraRisk?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q10}
                onChange={(e) => setResponses((p) => ({ ...p, q10: e.target.value }))}
                rows={3}
                placeholder="Ex: A fragmenta&#231;&#227;o institucional aumenta a vulnerabilidade &#224; dengue em munic&#237;pios de m&#233;dio porte..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">11.</span> Que dados ou funcionalidades faltam para que a ferramenta seja mais &uacute;til para voc&ecirc;?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q11}
                onChange={(e) => setResponses((p) => ({ ...p, q11: e.target.value }))}
                rows={3}
                placeholder="Descreva dados, vari&#225;veis ou funcionalidades que agregariam valor..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-3">
                <span className="font-bold text-teal-600">12.</span> Que institui&ccedil;&otilde;es ou redes do seu contexto se beneficiariam desta ferramenta? (Indique at&eacute; 5)
              </label>
              <CollaboratorTable
                value={responses.q12}
                onChange={(v) => setResponses((p) => ({ ...p, q12: v }))}
                disabled={disabled}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">13.</span> Que configura&ccedil;&atilde;o voc&ecirc; entende que deveria existir para articular melhor o uso de evid&ecirc;ncias na elabora&ccedil;&atilde;o de pol&iacute;ticas p&uacute;blicas vinculadas &agrave; mudan&ccedil;a clim&aacute;tica?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q13}
                onChange={(e) => setResponses((p) => ({ ...p, q13: e.target.value }))}
                rows={3}
                placeholder="Descreva a configura&#231;&#227;o ideal..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
          </div>
        </section>

        {/* ── BLOCO III — Próximos passos ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-4 p-4 rounded-lg bg-purple-50 border border-purple-200">
            <p className="text-xs font-semibold text-purple-500 uppercase tracking-wide">Bloco III &mdash; Pr&oacute;ximos passos</p>
            <p className="text-sm text-purple-700 mt-1 font-medium">O que vem depois?</p>
          </div>
          <LikertItem n={14} label="Tenho interesse em participar de um piloto com o TerraRisk." value={responses.ps14} onChange={(v) => setLikert('ps14', v)} disabled={disabled} />
          <LikertItem n={15} label="Identifico um contexto espec\u00edfico onde aplicar a ferramenta no curto prazo." value={responses.ps15} onChange={(v) => setLikert('ps15', v)} disabled={disabled} />
          <div className="py-3 mt-2">
            <div className="flex items-start gap-2">
              <span className="text-xs font-bold text-gray-400 mt-0.5 w-5 shrink-0">16.</span>
              <div className="flex-1">
                <p className="text-sm text-gray-700 mb-2">Autorizo o uso das minhas respostas para melhoria da ferramenta.</p>
                <div className="flex gap-4">
                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => setResponses((p) => ({ ...p, q16: true }))}
                    className={`px-6 py-2 rounded-lg text-sm font-semibold border-2 transition-all
                      ${responses.q16 === true
                        ? 'bg-purple-600 border-purple-600 text-white'
                        : 'border-gray-300 text-gray-500 hover:border-purple-400'
                      }
                      ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                  >
                    Sim
                  </button>
                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => setResponses((p) => ({ ...p, q16: false }))}
                    className={`px-6 py-2 rounded-lg text-sm font-semibold border-2 transition-all
                      ${responses.q16 === false
                        ? 'bg-gray-500 border-gray-500 text-white'
                        : 'border-gray-300 text-gray-500 hover:border-gray-400'
                      }
                      ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                  >
                    N&atilde;o
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Submit ── */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
            {error}
          </div>
        )}

        <div className="flex flex-col items-center gap-3 pb-8">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={disabled}
            className="px-8 py-3 bg-purple-600 text-white rounded-lg font-semibold text-sm hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {submitting ? 'Enviando...' : 'Enviar Avalia\u00e7\u00e3o'}
          </button>
          <p className="text-xs text-gray-400 text-center">
            Suas respostas s&atilde;o vinculadas apenas ao grupo <strong>{group?.name}</strong>.
          </p>
          <p className="text-xs text-gray-300 italic">
            ITECS v2.0 &middot; TerraX &middot; Dados anonimizados
          </p>
        </div>

      </div>
    </div>
  );
}
