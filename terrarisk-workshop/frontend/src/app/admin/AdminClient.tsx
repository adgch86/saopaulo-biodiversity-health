'use client';

import { useState, useEffect, useCallback, Fragment } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import LanguageSelector from '@/components/LanguageSelector';
import type { AdminStats, GroupStats } from '@/lib/types';

interface ITECSRow {
  id: number;
  group_id: string;
  group_name: string | null;
  participant_id: string;
  // Bloco I — Experiência (Likert 1-7)
  exp1: number; exp2: number; exp3: number; exp4: number;
  exp5: number; exp6: number; exp7: number; exp8: number;
  // Bloco II — Aplicação prática
  q9: string; q10: string; q11: string;
  q12: { nameOrInstitution: string; topic: string; frequency: string }[];
  q13: string;
  // Bloco III — Próximos passos
  ps14: number; ps15: number;
  q16: boolean;
  // Meta
  version: string;
  layers_purchased: string[];
  credits_spent: number;
  ranking_changed: boolean;
  actions_selected: string[];
  submitted_at: string;
}
import type { Locale } from '@/i18n/config';

export default function AdminClient() {
  const t = useTranslations('admin');
  const tc = useTranslations('common');
  const tl = useTranslations('landing');

  const AREA_LABELS: Record<string, string> = {
    academia: tl('areaAcademia'),
    government: tl('areaGovernment'),
    ngo: tl('areaNgo'),
    private: tl('areaPrivate'),
    student: tl('areaStudent'),
    other: tl('areaOther'),
  };

  const EXP_LABELS: Record<string, string> = {
    none: tl('expNone'),
    basic: tl('expBasic'),
    intermediate: tl('expIntermediate'),
    advanced: tl('expAdvanced'),
  };
  const locale = useLocale() as Locale;
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [itecs, setItecs] = useState<ITECSRow[]>([]);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const adminHeaders = { 'X-API-Key': 'terrarisk-admin-2026' };

  const fetchStats = useCallback(async () => {
    try {
      const [statsRes, itecsRes] = await Promise.all([
        fetch('/api/admin/stats', { headers: adminHeaders }),
        fetch('/api/workshop/survey/admin/results'),
      ]);
      const data = await statsRes.json();
      const itecsData = await itecsRes.json();
      setStats(data);
      setItecs(itecsData);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchStats();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  const handleResetCredits = async (groupId: string) => {
    setActionLoading(groupId);
    try {
      await fetch(`/api/admin/reset/${groupId}`, { method: 'POST', headers: adminHeaders });
      await fetchStats();
    } catch (err) {
      console.error('Failed to reset credits:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteGroup = async (groupId: string) => {
    if (!confirm('Delete this group?')) return;

    setActionLoading(groupId);
    try {
      await fetch(`/api/admin/groups/${groupId}`, { method: 'DELETE', headers: adminHeaders });
      await fetchStats();
    } catch (err) {
      console.error('Failed to delete group:', err);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-500">{tc('error')}</p>
      </div>
    );
  }

  // ── ITECS v2 helpers ───────────────────────────────────────────────────────

  const avg = (vals: number[]) => {
    const valid = vals.filter((v) => v > 0);
    return valid.length ? valid.reduce((a, b) => a + b, 0) / valid.length : 0;
  };

  const blockAvg = (rows: ITECSRow[], keys: (keyof ITECSRow)[]) => {
    if (!rows.length) return 0;
    return avg(rows.map((r) => avg(keys.map((k) => (r[k] as number) || 0))));
  };

  const BLOCKS = [
    { id: 'EXP', label: 'Experiência com TerraRisk', keys: ['exp1','exp2','exp3','exp4','exp5','exp6','exp7','exp8'] as (keyof ITECSRow)[], color: 'bg-purple-500' },
    { id: 'PS',  label: 'Próximos Passos',            keys: ['ps14','ps15'] as (keyof ITECSRow)[], color: 'bg-teal-500' },
  ];

  const QUESTION_LABELS: Record<string, string> = {
    exp1: '1. Entender melhor o território',
    exp2: '2. Identificar relações entre variáveis',
    exp3: '3. Dados relevantes para o trabalho',
    exp4: '4. Escala municipal adequada',
    exp5: '5. Resultados coerentes com o território',
    exp6: '6. Útil para apoiar decisões',
    exp7: '7. Usaria no trabalho',
    exp8: '8. Recomendaria a colegas',
    ps14: '14. Interesse em piloto',
    ps15: '15. Contexto para aplicar no curto prazo',
  };

  const exportCSV = () => {
    if (!itecs.length) return;
    const headers = [
      'participant_id','group_id','group_name',
      'exp1','exp2','exp3','exp4','exp5','exp6','exp7','exp8',
      'q9','q10','q11','q13',
      'ps14','ps15','q16',
      'layers_purchased','credits_spent','ranking_changed','actions_selected','submitted_at'
    ];
    const rows = itecs.map((r) => headers.map((h) => {
      const v = r[h as keyof ITECSRow];
      if (Array.isArray(v)) return `"${v.join(';')}"`;
      if (typeof v === 'string' && v.includes(',')) return `"${v.replace(/"/g,'""')}"`;
      return v ?? '';
    }).join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `itecs_v2_results_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">{t('title')}</h1>
            <p className="text-gray-500">{t('subtitle')}</p>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSelector currentLocale={locale} />
            <Button onClick={fetchStats} variant="outline">
              {t('refresh')}
            </Button>
          </div>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-500">{t('totalGroups')}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-purple-600">{stats.totalGroups}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-500">{t('totalPurchases')}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-blue-600">{stats.totalPurchases}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-500">{t('creditsSpent')}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-green-600">{stats.creditsSpent}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-500">{t('avgLayersPerGroup')}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-orange-600">
                {stats.totalGroups > 0
                  ? (stats.totalPurchases / stats.totalGroups).toFixed(1)
                  : '0'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Popular layers */}
        <Card>
          <CardHeader>
            <CardTitle>{t('popularLayers')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {stats.popularLayers.slice(0, 10).map((item, i) => (
                <Badge key={item.layerId} variant={i < 3 ? 'default' : 'secondary'}>
                  {item.layerId} ({item.count})
                </Badge>
              ))}
              {stats.popularLayers.length === 0 && (
                <p className="text-gray-500">{t('noPurchases')}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Groups table */}
        <Card>
          <CardHeader>
            <CardTitle>{t('groups')} ({stats.groupStats.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3 font-medium text-gray-500">{t('name')}</th>
                    <th className="text-left py-2 px-3 font-medium text-gray-500">{t('profile')}</th>
                    <th className="text-center py-2 px-3 font-medium text-gray-500">{t('credits')}</th>
                    <th className="text-center py-2 px-3 font-medium text-gray-500">{t('layersCount')}</th>
                    <th className="text-left py-2 px-3 font-medium text-gray-500">{t('lastActivity')}</th>
                    <th className="text-right py-2 px-3 font-medium text-gray-500">{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.groupStats.map((group: GroupStats) => (
                    <tr key={group.id} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-3 font-medium">
                        {group.name}
                        {group.numParticipants && (
                          <span className="text-xs text-gray-400 ml-1">({group.numParticipants}p)</span>
                        )}
                      </td>
                      <td className="py-2 px-3">
                        <div className="flex flex-wrap gap-1">
                          {group.professionalArea && (
                            <Badge variant="outline" className="text-xs">
                              {AREA_LABELS[group.professionalArea] ?? group.professionalArea}
                            </Badge>
                          )}
                          {group.environmentalExperience && (
                            <Badge variant="secondary" className="text-xs">
                              {EXP_LABELS[group.environmentalExperience] ?? group.environmentalExperience}
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-2 px-3 text-center">
                        <Badge
                          variant={group.credits > 5 ? 'default' : group.credits > 0 ? 'secondary' : 'destructive'}
                        >
                          {group.credits}
                        </Badge>
                      </td>
                      <td className="py-2 px-3 text-center">{group.purchasedCount}</td>
                      <td className="py-2 px-3 text-sm text-gray-500">
                        {new Date(group.lastActivity).toLocaleString()}
                      </td>
                      <td className="py-2 px-3 text-right">
                        <div className="flex gap-2 justify-end">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResetCredits(group.id)}
                            disabled={actionLoading === group.id}
                          >
                            {actionLoading === group.id ? '...' : t('resetCredits')}
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteGroup(group.id)}
                            disabled={actionLoading === group.id}
                          >
                            {tc('delete')}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {stats.groupStats.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-500">
                        {t('noGroups')}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
        {/* ── ITECS v2.0 Results ── */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Avaliação TerraRisk (ITECS v2.0)</CardTitle>
                <p className="text-sm text-gray-500 mt-1">
                  {itecs.length} resposta{itecs.length !== 1 ? 's' : ''} individuai{itecs.length !== 1 ? 's' : ''}
                  {itecs.length > 0 && ` · ${new Set(itecs.map(r => r.group_id)).size} grupo${new Set(itecs.map(r => r.group_id)).size !== 1 ? 's' : ''}`}
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={exportCSV} disabled={!itecs.length}>
                Exportar CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">

            {itecs.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-8">Nenhuma resposta ainda.</p>
            ) : (
              <>
                {/* Promedios por bloco */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Médias por Bloco (escala 1–7)</p>
                  <div className="space-y-2">
                    {BLOCKS.map((block) => {
                      const mean = blockAvg(itecs, block.keys);
                      const pct = ((mean - 1) / 6) * 100;
                      return (
                        <div key={block.id} className="flex items-center gap-3">
                          <span className="text-xs font-bold text-gray-500 w-8">{block.id}</span>
                          <span className="text-xs text-gray-600 w-52 shrink-0">{block.label}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                            <div
                              className={`h-3 rounded-full transition-all ${block.color}`}
                              style={{ width: `${Math.max(pct, 2)}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-gray-700 w-8 text-right">
                            {mean.toFixed(1)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Per-question averages */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Médias por Pergunta</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {Object.entries(QUESTION_LABELS).map(([key, label]) => {
                      const mean = avg(itecs.map((r) => (r[key as keyof ITECSRow] as number) || 0));
                      const color = mean >= 5.5 ? 'text-green-600' : mean >= 3.5 ? 'text-amber-600' : 'text-red-500';
                      return (
                        <div key={key} className="flex items-center gap-2 text-xs">
                          <span className={`font-bold w-8 text-right ${color}`}>{mean.toFixed(1)}</span>
                          <span className="text-gray-600">{label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Tabla de respuestas */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Respostas Individuais</p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-gray-50">
                          <th className="text-left py-2 px-3 font-medium text-gray-500">Grupo</th>
                          {BLOCKS.map((b) => (
                            <th key={b.id} className="text-center py-2 px-2 font-medium text-gray-500 w-12">{b.id}</th>
                          ))}
                          <th className="text-center py-2 px-2 font-medium text-gray-500">Q16</th>
                          <th className="text-center py-2 px-2 font-medium text-gray-500">Camadas</th>
                          <th className="text-left py-2 px-3 font-medium text-gray-500">Data</th>
                          <th className="py-2 px-2" />
                        </tr>
                      </thead>
                      <tbody>
                        {itecs.map((row) => {
                          const pid = row.participant_id;
                          const isOpen = expandedRow === pid;
                          return (
                            <Fragment key={pid}>
                              <tr className="border-b hover:bg-gray-50">
                                <td className="py-2 px-3 font-medium text-xs">
                                  {row.group_name || row.group_id.slice(0, 8)}
                                </td>
                                {BLOCKS.map((b) => {
                                  const mean = avg(b.keys.map((k) => (row[k] as number) || 0));
                                  const color = mean >= 5.5 ? 'text-green-600' : mean >= 3.5 ? 'text-amber-600' : 'text-red-500';
                                  return (
                                    <td key={b.id} className={`py-2 px-2 text-center text-xs font-semibold ${color}`}>
                                      {mean.toFixed(1)}
                                    </td>
                                  );
                                })}
                                <td className="py-2 px-2 text-center text-xs">
                                  {row.q16 ? (
                                    <span className="text-green-600 font-bold">Sim</span>
                                  ) : (
                                    <span className="text-gray-400">Não</span>
                                  )}
                                </td>
                                <td className="py-2 px-2 text-center text-xs">{row.credits_spent ?? '-'}</td>
                                <td className="py-2 px-3 text-xs text-gray-400">
                                  {new Date(row.submitted_at).toLocaleDateString()}
                                </td>
                                <td className="py-2 px-2">
                                  <button
                                    onClick={() => setExpandedRow(isOpen ? null : pid)}
                                    className="text-xs text-purple-500 hover:text-purple-700 underline"
                                  >
                                    {isOpen ? 'fechar' : 'ver'}
                                  </button>
                                </td>
                              </tr>

                              {isOpen && (
                                <tr className="bg-purple-50">
                                  <td colSpan={7} className="px-4 py-4">
                                    <div className="space-y-4 text-sm">

                                      {/* Likert detalhado */}
                                      <div>
                                        <p className="text-xs font-semibold text-gray-500 mb-2">Bloco I — Experiência com TerraRisk</p>
                                        <div className="flex flex-wrap gap-2">
                                          {(['exp1','exp2','exp3','exp4','exp5','exp6','exp7','exp8'] as (keyof ITECSRow)[]).map((k) => {
                                            const val = row[k] as number;
                                            const color = val >= 5 ? 'border-green-300 bg-green-50' : val >= 3 ? 'border-amber-300 bg-amber-50' : 'border-red-300 bg-red-50';
                                            return (
                                              <span key={String(k)} className={`text-xs border rounded px-2 py-1 text-gray-700 ${color}`}>
                                                {String(k).replace('exp', 'Q')}: <strong>{val}</strong>
                                              </span>
                                            );
                                          })}
                                        </div>
                                      </div>
                                      <div>
                                        <p className="text-xs font-semibold text-gray-500 mb-2">Bloco III — Próximos Passos</p>
                                        <div className="flex flex-wrap gap-2">
                                          <span className="text-xs border rounded px-2 py-1 text-gray-700 bg-white">
                                            Q14 (Piloto): <strong>{row.ps14}</strong>
                                          </span>
                                          <span className="text-xs border rounded px-2 py-1 text-gray-700 bg-white">
                                            Q15 (Contexto): <strong>{row.ps15}</strong>
                                          </span>
                                          <span className="text-xs border rounded px-2 py-1 text-gray-700 bg-white">
                                            Q16 (Autoriza): <strong>{row.q16 ? 'Sim' : 'Não'}</strong>
                                          </span>
                                        </div>
                                      </div>

                                      {/* Perguntas abertas */}
                                      {[
                                        { label: 'Q9 — Problema concreto', val: row.q9 },
                                        { label: 'Q10 — Hipótese causal', val: row.q10 },
                                        { label: 'Q11 — Dados/funcionalidades faltantes', val: row.q11 },
                                        { label: 'Q13 — Configuração para políticas públicas', val: row.q13 },
                                      ].filter(({ val }) => val).map(({ label, val }) => (
                                        <div key={label}>
                                          <p className="text-xs font-semibold text-gray-500">{label}</p>
                                          <p className="text-xs text-gray-700 mt-0.5 bg-white rounded p-2 border">{val}</p>
                                        </div>
                                      ))}

                                      {/* Q12 Rede */}
                                      {row.q12?.filter(c => c.nameOrInstitution).length > 0 && (
                                        <div>
                                          <p className="text-xs font-semibold text-gray-500 mb-1">Q12 — Instituições/redes beneficiadas</p>
                                          <div className="flex flex-wrap gap-2">
                                            {row.q12.filter(c => c.nameOrInstitution).map((c, i) => (
                                              <span key={i} className="text-xs bg-white border rounded px-2 py-1 text-gray-700">
                                                <strong>{c.nameOrInstitution}</strong> · {c.topic} · {c.frequency}
                                              </span>
                                            ))}
                                          </div>
                                        </div>
                                      )}

                                      {/* Metadata */}
                                      <div className="text-xs text-gray-400 flex flex-wrap gap-4">
                                        <span>Camadas: {Array.isArray(row.layers_purchased) ? row.layers_purchased.join(', ') || '–' : '–'}</span>
                                        <span>Ações: {Array.isArray(row.actions_selected) ? row.actions_selected.join(', ') || '–' : '–'}</span>
                                        <span>Créditos gastos: {row.credits_spent}</span>
                                        <span>Ranking mudou: {row.ranking_changed ? 'Sim' : 'Não'}</span>
                                      </div>

                                    </div>
                                  </td>
                                </tr>
                              )}
                            </Fragment>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
