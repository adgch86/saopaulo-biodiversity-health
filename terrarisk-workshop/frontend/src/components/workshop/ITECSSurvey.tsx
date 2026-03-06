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

// ─── Block header ─────────────────────────────────────────────────────────────

function BlockHeader({
  title,
  anchor,
  question,
}: {
  title: string;
  anchor: string;
  question: string;
}) {
  return (
    <div className="mb-4 p-4 rounded-lg bg-purple-50 border border-purple-200">
      <p className="text-xs font-semibold text-purple-500 uppercase tracking-wide">{title}</p>
      <p className="text-xs text-purple-400 mt-0.5 italic">{anchor}</p>
      <p className="text-sm text-purple-700 mt-1 font-medium">{question}</p>
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
  revised,
}: {
  n: number;
  label: string;
  value: number;
  onChange: (v: number) => void;
  disabled: boolean;
  revised?: boolean;
}) {
  return (
    <div className={`py-3 border-b border-gray-100 last:border-0 ${value === 0 && !disabled ? 'bg-amber-50 rounded' : ''}`}>
      <div className="flex items-start gap-2">
        <span className="text-xs font-bold text-gray-400 mt-0.5 w-5 shrink-0">{n}.</span>
        <div className="flex-1">
          <p className="text-sm text-gray-700">
            {label}
            {revised && <span className="ml-1 text-xs text-purple-400 italic">(v1.2)</span>}
          </p>
          <LikertScale value={value} onChange={onChange} disabled={disabled} />
        </div>
      </div>
    </div>
  );
}

// ─── Collaborator table ───────────────────────────────────────────────────────

const FREQ_OPTIONS: { value: ITECSCollaborator['frequency']; label: string }[] = [
  { value: 'more_than_monthly', label: 'Mais de uma vez por mês' },
  { value: 'monthly', label: 'Uma vez por mês' },
  { value: 'yearly', label: 'Uma vez por ano' },
  { value: 'sporadic', label: 'Esporádica' },
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
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600">Pessoa / Instituição / Rede</th>
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600">Tema de colaboração</th>
            <th className="text-left p-2 border border-gray-200 text-xs text-gray-600">Frequência</th>
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
                  placeholder="Nome ou instituição"
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
    tc1: 0, tc2: 0, tc3: 0, tc4: 0, tc5: 0,
    ra6: 0, ra7: 0, ra8: 0,
    pf9: 0, pf10: 0, pf11: 0, pf12: 0,
    csp13: 0, csp14: 0, csp15: 0, csp16: 0,
    ia17: 0, ia18: 0, ia19: 0, ia20: 0,
    ap21: 0, ap22: 0, ap23: 0, ap24: 0, ap25: 0,
    q26: '', q27: '',
    q28: Array.from({ length: 5 }, () => ({ nameOrInstitution: '', topic: '', frequency: 'sporadic' as const })),
    q29: '', q30: '',
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

  // Generate participantId once on mount
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
      'tc1','tc2','tc3','tc4','tc5',
      'ra6','ra7','ra8',
      'pf9','pf10','pf11','pf12',
      'csp13','csp14','csp15','csp16',
      'ia17','ia18','ia19','ia20',
      'ap21','ap22','ap23','ap24','ap25',
    ];
    return likertFields.filter((f) => (responses[f] as number) === 0);
  };

  const handleSubmit = async () => {
    const missing = missingLikert();
    if (missing.length > 0) {
      setError(`Por favor, responda todos os itens Likert (${missing.length} pendente${missing.length > 1 ? 's' : ''}).`);
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
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Avaliação enviada</h2>
          <p className="text-gray-600 mb-6">
            Obrigado pela sua participação. Suas respostas foram registradas e serão utilizadas
            exclusivamente para fins de autoavaliação e otimização da ferramenta.
          </p>
          <div className="text-xs text-gray-400 italic">
            ITECS v1.2 · TerraX Research · Dados anonimizados
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
              <h1 className="text-xl lg:text-2xl font-bold text-gray-800">ITECS</h1>
              <p className="text-xs text-gray-400">Instrumento de Avaliação de Coerência Sistêmica · v1.2</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 bg-white rounded-lg p-4 border border-gray-200">
            Este instrumento avalia sua experiência com a ferramenta TerraRisk e o marco analítico TerraX.
            Não há respostas certas ou erradas. Todas as respostas são utilizadas exclusivamente
            para fins de autoavaliação e otimização da ferramenta. São 25 perguntas de seleção e 5 descritivas. O preenchimento leva aproximadamente 12 minutos.
          </p>
        </div>

        {/* Likert instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
          <strong>Escala Likert:</strong> Para cada afirmação, selecione de <strong>1</strong> (Discordo totalmente)
          a <strong>7</strong> (Concordo totalmente).
        </div>

        {/* ── BLOCO I — Transformação Cognitiva ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <BlockHeader
            title="Bloco I — Transformação Cognitiva (TC)"
            anchor="Âncora conceitual: reorganização epistêmica do participante"
            question="Como mudou minha forma de compreender o território?"
          />
          <LikertItem n={1} label="Minha compreensão do sistema territorial ampliou-se significativamente." value={responses.tc1} onChange={(v) => setLikert('tc1', v)} disabled={disabled} />
          <LikertItem n={2} label="Agora identifico relações sistêmicas que antes não considerava." value={responses.tc2} onChange={(v) => setLikert('tc2', v)} disabled={disabled} />
          <LikertItem n={3} label="O marco apresentado modificou minha forma de analisar problemas complexos." value={responses.tc3} onChange={(v) => setLikert('tc3', v)} disabled={disabled} />
          <LikertItem n={4} label="Minha capacidade de analisar problemas territoriais de forma integrada aumentou após esta experiência." value={responses.tc4} onChange={(v) => setLikert('tc4', v)} disabled={disabled} revised />
          <LikertItem n={5} label="Reconheço padrões estruturais que anteriormente não observava." value={responses.tc5} onChange={(v) => setLikert('tc5', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO II — Robustez Analítica ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <BlockHeader
            title="Bloco II — Robustez Analítica"
            anchor="Avalie a qualidade metodológica e a solidez dos resultados apresentados."
            question=""
          />
          <LikertItem n={6} label="A seleção de variáveis foi metodologicamente adequada para capturar o nexo governança–biodiversidade–clima–saúde." value={responses.ra6} onChange={(v) => setLikert('ra6', v)} disabled={disabled} />
          <LikertItem n={7} label="A escala espacial utilizada (municipal) foi apropriada para a análise proposta." value={responses.ra7} onChange={(v) => setLikert('ra7', v)} disabled={disabled} />
          <LikertItem n={8} label="Os resultados apresentaram plausibilidade causal, não apenas correlações estatísticas." value={responses.ra8} onChange={(v) => setLikert('ra8', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO III — Potencial da Ferramenta ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <BlockHeader
            title="Bloco III — Potencial da Ferramenta"
            anchor="Avalie o impacto do TerraRisk como instrumento de apoio à tomada de decisão e à pesquisa."
            question=""
          />
          <LikertItem n={9} label="A ferramenta ajudou a estruturar o problema em termos causais (não apenas descritivos)." value={responses.pf9} onChange={(v) => setLikert('pf9', v)} disabled={disabled} />
          <LikertItem n={10} label="A interação com o TerraRisk estimulou novas perguntas e hipóteses que eu não havia considerado." value={responses.pf10} onChange={(v) => setLikert('pf10', v)} disabled={disabled} revised />
          <LikertItem n={11} label="A abordagem multi-domínio favoreceu raciocínio sistêmico sobre o território." value={responses.pf11} onChange={(v) => setLikert('pf11', v)} disabled={disabled} />
          <LikertItem n={12} label="A ferramenta favorece colaboração entre disciplinas que normalmente trabalham em silos." value={responses.pf12} onChange={(v) => setLikert('pf12', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO IV — Coerência Sistêmica Percebida ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <BlockHeader
            title="Bloco IV — Coerência Sistêmica Percebida (CSP)"
            anchor="Âncora conceitual: percepção do sistema externo"
            question="Como vejo o território agora?"
          />
          <LikertItem n={13} label="O sistema territorial em que atuo possui componentes interdependentes que afetam as decisões." value={responses.csp13} onChange={(v) => setLikert('csp13', v)} disabled={disabled} revised />
          <LikertItem n={14} label="Identifico claramente pontos de fragmentação institucional." value={responses.csp14} onChange={(v) => setLikert('csp14', v)} disabled={disabled} />
          <LikertItem n={15} label="Compreendo como integrar escalas municipais e estaduais." value={responses.csp15} onChange={(v) => setLikert('csp15', v)} disabled={disabled} />
          <LikertItem n={16} label="Percebo que a coordenação estrutural é possível." value={responses.csp16} onChange={(v) => setLikert('csp16', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO V — Intenção de Aplicação ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <BlockHeader
            title="Bloco V — Intenção de Aplicação (IA)"
            anchor="Âncora conceitual: viabilidade percebida real"
            question="Posso fazer isso?"
          />
          <LikertItem n={17} label="Consigo identificar um contexto específico onde aplicar a abordagem." value={responses.ia17} onChange={(v) => setLikert('ia17', v)} disabled={disabled} />
          <LikertItem n={18} label="Considero viável sua implementação no meu ambiente profissional." value={responses.ia18} onChange={(v) => setLikert('ia18', v)} disabled={disabled} />
          <LikertItem n={19} label="Estou disposto/a a explorar sua aplicação no curto prazo." value={responses.ia19} onChange={(v) => setLikert('ia19', v)} disabled={disabled} />
          <LikertItem n={20} label="Vejo benefícios concretos em sua adoção." value={responses.ia20} onChange={(v) => setLikert('ia20', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO VI — Ativação Proativa ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <BlockHeader
            title="Bloco VI — Ativação Proativa (AP)"
            anchor="Âncora conceitual: disposição para agir"
            question="Vou fazer isso?"
          />
          <LikertItem n={21} label="Tenho interesse em participar de um piloto relacionado." value={responses.ap21} onChange={(v) => setLikert('ap21', v)} disabled={disabled} />
          <LikertItem n={22} label="Assumiria um papel ativo em um processo de implementação." value={responses.ap22} onChange={(v) => setLikert('ap22', v)} disabled={disabled} />
          <LikertItem n={23} label="Considero necessária a ação após esta experiência." value={responses.ap23} onChange={(v) => setLikert('ap23', v)} disabled={disabled} />
          <LikertItem n={24} label="Recomendaria esta abordagem a atores estratégicos." value={responses.ap24} onChange={(v) => setLikert('ap24', v)} disabled={disabled} />
          <LikertItem n={25} label="Estou disposto/a a continuar a conversa institucionalmente." value={responses.ap25} onChange={(v) => setLikert('ap25', v)} disabled={disabled} />
        </section>

        {/* ── BLOCO VII — Coprodução e Uso de Evidência ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-4 p-4 rounded-lg bg-teal-50 border border-teal-200">
            <p className="text-xs font-semibold text-teal-600 uppercase tracking-wide">Bloco VII — Coprodução e Uso de Evidência</p>
            <p className="text-xs text-teal-500 mt-0.5 italic">
              Estas perguntas exploram como a experiência com o TerraRisk pode influenciar práticas de uso de evidência e colaboração entre ciência e política.
            </p>
          </div>
          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">26.</span> Após a experiência com o TerraRisk, que caminhos concretos você identifica para melhorar o uso de evidência científica na gestão ambiental do seu município ou instituição?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q26}
                onChange={(e) => setResponses((p) => ({ ...p, q26: e.target.value }))}
                rows={4}
                placeholder="Descreva caminhos concretos..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">27.</span> Que barreiras específicas você enfrenta hoje para promover a coprodução entre pesquisadores e tomadores de decisão? O TerraRisk ajudou a visualizar como superar alguma delas?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q27}
                onChange={(e) => setResponses((p) => ({ ...p, q27: e.target.value }))}
                rows={4}
                placeholder="Descreva barreiras e se a ferramenta ajudou..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
          </div>
        </section>

        {/* ── BLOCO VIII — Rede de Colaboradores ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-4 p-4 rounded-lg bg-teal-50 border border-teal-200">
            <p className="text-xs font-semibold text-teal-600 uppercase tracking-wide">Bloco VIII — Rede de Colaboradores</p>
            <p className="text-xs text-teal-500 mt-0.5 italic">
              Mapeamento das redes existentes e potencial de conexão entre instituições participantes.
            </p>
          </div>
          <label className="text-sm font-medium text-gray-700 block mb-3">
            <span className="font-bold text-teal-600">28.</span> Além dos participantes deste workshop, com quais instituições ou redes você já colabora em temas de governança ambiental, biodiversidade ou saúde pública? (Indique até 5)
          </label>
          <CollaboratorTable
            value={responses.q28}
            onChange={(v) => setResponses((p) => ({ ...p, q28: v }))}
            disabled={disabled}
          />
        </section>

        {/* ── BLOCO IX — Próximos Passos ── */}
        <section className="bg-white rounded-xl shadow-sm p-6">
          <div className="mb-4 p-4 rounded-lg bg-teal-50 border border-teal-200">
            <p className="text-xs font-semibold text-teal-600 uppercase tracking-wide">Bloco IX — Próximos Passos</p>
            <p className="text-xs text-teal-500 mt-0.5 italic">
              Suas respostas ajudarão a orientar o desenvolvimento futuro da ferramenta e novas linhas de pesquisa.
            </p>
          </div>
          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">29.</span> Que hipótese causal específica você investigaria utilizando o TerraRisk?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q29}
                onChange={(e) => setResponses((p) => ({ ...p, q29: e.target.value }))}
                rows={3}
                placeholder="Ex: A fragmentação institucional aumenta a vulnerabilidade à dengue em municípios de médio porte..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                <span className="font-bold text-teal-600">30.</span> Que variável ou dimensão deveria ser incorporada, ou aprimorada ao modelo para fortalecer a análise?
              </label>
              <textarea
                disabled={disabled}
                value={responses.q30}
                onChange={(e) => setResponses((p) => ({ ...p, q30: e.target.value }))}
                rows={3}
                placeholder="Descreva a variável ou dimensão e por que seria relevante..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-400 focus:border-transparent disabled:bg-gray-50 resize-none"
              />
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
            {submitting ? 'Enviando...' : 'Enviar Avaliação'}
          </button>
          <p className="text-xs text-gray-400 text-center">
            Suas respostas são confidenciais e vinculadas apenas ao grupo <strong>{group?.name}</strong>.
          </p>
          <p className="text-xs text-gray-300 italic">
            ITECS v1.2 · TerraX Research · Uso restrito a fins de autoavaliação e otimização · Dados anonimizados
          </p>
          <p className="text-xs text-gray-300 italic">
            Correspondência TRLM v1.4: TC→P2+L5 · CSP→P3+L4 · IA→P4+L7 · AP→Dinâmica Ativação+Loop L7→L1
          </p>
        </div>

      </div>
    </div>
  );
}
