'use client';

import { useTranslations } from 'next-intl';
import { useWorkshopStore } from '@/lib/store';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { CATEGORY_CONFIG } from '@/lib/types';

interface Props {
  onSubmit: (actionIds: string[]) => void;
}

export default function ActionsSelector({ onSubmit }: Props) {
  const t = useTranslations('workshopFlow');
  const tActions = useTranslations('actionNames');
  const tDesc = useTranslations('actionDescriptions');
  const { pearcActions, selectedActions, toggleAction } = useWorkshopStore();

  const handleSubmit = () => {
    if (selectedActions.length > 0) {
      onSubmit(selectedActions);
    }
  };

  const getCategoryColor = (category: string) => {
    const config = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG];
    return config ? config.color : '#6B7280';
  };

  const getCategoryBgColor = (category: string) => {
    const config = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG];
    return config ? config.bgColor : 'bg-gray-100';
  };

  const renderEvidenceStars = (avgEvidence: number) => {
    const stars = Math.round(avgEvidence);
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full ${
              i <= stars ? 'bg-yellow-500' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">{t('selectActions')}</h2>
        <p className="text-gray-600">
          {selectedActions.length} {t('actionsSelected')}
        </p>
      </div>

      <ScrollArea className="flex-1 mb-4">
        <div className="grid grid-cols-1 gap-3 pr-4">
          {pearcActions.map((action) => {
            const isSelected = selectedActions.includes(action.id);
            const linkedDimensions = Object.entries(action.links).filter(([, value]) => value > 0);

            return (
              <Card
                key={action.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  isSelected ? 'ring-2 ring-purple-400 shadow-md' : ''
                }`}
                onClick={() => toggleAction(action.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-1 transition-all ${
                        isSelected
                          ? 'bg-purple-600 border-purple-600'
                          : 'border-gray-300 hover:border-purple-400'
                      }`}
                    >
                      {isSelected && (
                        <svg
                          className="w-3 h-3 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold text-gray-800 text-sm">
                          {tActions(action.id)}
                        </h3>
                        <Badge
                          className={`${getCategoryBgColor(action.category)} text-xs ml-2`}
                          style={{ color: getCategoryColor(action.category) }}
                        >
                          {action.category}
                        </Badge>
                      </div>

                      <p className="text-xs text-gray-600 mb-3">{tDesc(action.id)}</p>

                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                            />
                          </svg>
                          <span>
                            {t('linksTo')} {linkedDimensions.length} {t('riskDimensions')}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span>{t('evidence')}:</span>
                          {renderEvidenceStars(action.avgEvidence)}
                        </div>
                      </div>

                      {linkedDimensions.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {linkedDimensions.map(([dimension]) => (
                            <Badge
                              key={dimension}
                              variant="outline"
                              className="text-xs"
                              style={{
                                borderColor: getCategoryColor(dimension),
                                color: getCategoryColor(dimension),
                              }}
                            >
                              {dimension}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </ScrollArea>

      <div className="pt-4 border-t border-gray-200">
        <Button
          className="w-full bg-purple-600 hover:bg-purple-700"
          disabled={selectedActions.length === 0}
          onClick={handleSubmit}
        >
          {t('viewResults')}
        </Button>
      </div>
    </div>
  );
}
