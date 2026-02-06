'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import LanguageSelector from '@/components/LanguageSelector';
import type { AdminStats, GroupStats } from '@/lib/types';
import type { Locale } from '@/i18n/config';

export default function AdminPage() {
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

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch('/api/admin/stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
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
      await fetch(`/api/admin/reset/${groupId}`, { method: 'POST' });
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
      await fetch(`/api/admin/groups/${groupId}`, { method: 'DELETE' });
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
      </div>
    </div>
  );
}
