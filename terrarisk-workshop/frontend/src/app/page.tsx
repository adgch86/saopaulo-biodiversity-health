'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations, useLocale } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import LanguageSelector from '@/components/LanguageSelector';
import type { Group } from '@/lib/types';
import type { Locale } from '@/i18n/config';

export default function Home() {
  const t = useTranslations('landing');
  const locale = useLocale() as Locale;
  const router = useRouter();
  const { group, setGroup } = useWorkshopStore();
  const [groupName, setGroupName] = useState('');
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already has group
  useEffect(() => {
    if (group) {
      router.push('/workshop');
    }
  }, [group, router]);

  // Fetch existing groups
  useEffect(() => {
    fetch('/api/groups')
      .then((res) => res.json())
      .then(setGroups)
      .catch(console.error);
  }, []);

  const handleCreateGroup = async () => {
    if (!groupName.trim()) {
      setError(t('errorNameRequired'));
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: groupName.trim() }),
      });

      if (!res.ok) throw new Error('Error');

      const newGroup = await res.json();
      setGroup(newGroup);
      router.push('/workshop');
    } catch {
      setError(t('errorCreateGroup'));
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGroup = async (groupId: string) => {
    setLoading(true);
    setError('');

    try {
      const res = await fetch(`/api/groups/${groupId}`);
      if (!res.ok) throw new Error('Error');

      const existingGroup = await res.json();
      setGroup(existingGroup);
      router.push('/workshop');
    } catch {
      setError(t('errorJoinGroup'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Language selector */}
        <div className="flex justify-end mb-4">
          <LanguageSelector currentLocale={locale} />
        </div>

        {/* Logo and title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl shadow-lg mb-4">
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">{t('title')}</h1>
          <p className="text-lg text-gray-600">{t('subtitle')}</p>
          <p className="text-sm text-gray-500 mt-2">{t('description')}</p>
        </div>

        {/* Main card */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>{t('welcome')}</CardTitle>
            <CardDescription>{t('welcomeDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="create">
              <TabsList className="w-full mb-4">
                <TabsTrigger value="create" className="flex-1">
                  {t('createGroup')}
                </TabsTrigger>
                <TabsTrigger value="join" className="flex-1">
                  {t('joinGroup')}
                </TabsTrigger>
              </TabsList>

              <TabsContent value="create">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      {t('groupName')}
                    </label>
                    <input
                      type="text"
                      value={groupName}
                      onChange={(e) => setGroupName(e.target.value)}
                      placeholder={t('groupNamePlaceholder')}
                      className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      onKeyDown={(e) => e.key === 'Enter' && handleCreateGroup()}
                    />
                  </div>

                  {error && <p className="text-sm text-red-500">{error}</p>}

                  <Button
                    className="w-full"
                    onClick={handleCreateGroup}
                    disabled={loading}
                  >
                    {loading ? t('creating') : t('createAndStart')}
                  </Button>

                  <div className="text-center text-sm text-gray-500">
                    {t('initialCredits', { credits: 10 })}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="join">
                <div className="space-y-4">
                  {groups.length === 0 ? (
                    <p className="text-center text-gray-500 py-4">
                      {t('noGroups')}
                    </p>
                  ) : (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {groups.map((g) => (
                        <div
                          key={g.id}
                          className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition"
                        >
                          <div>
                            <p className="font-medium">{g.name}</p>
                            <p className="text-xs text-gray-500">
                              {g.credits} {t('credits')} - {g.purchasedLayers.length} {t('layers')}
                            </p>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleJoinGroup(g.id)}
                            disabled={loading}
                          >
                            {t('join')}
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-500">
          <p>{t('footer1')}</p>
          <p>{t('footer2')}</p>
        </div>
      </div>
    </main>
  );
}
