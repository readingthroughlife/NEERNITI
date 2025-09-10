import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import { Label } from '../ui/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { Button } from '../ui/Button';
import { Download } from 'lucide-react';
import { translations } from '../i18n';

const DownloadDataPage = ({ language }) => {
  const t = translations[language];

  const states = ["Maharashtra", "Punjab", "Haryana", "Rajasthan", "Uttar Pradesh"];
  const years = ["2024", "2023", "2022", "2021", "2020"];

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">{t.downloadTitle}</h1>
        <p className="text-muted-foreground">{t.downloadDescription}</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Create Report</CardTitle>
          <CardDescription>All fields are mandatory to generate a report.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="state-select">{t.selectState}</Label>
            <Select>
              <SelectTrigger id="state-select">
                <SelectValue placeholder={t.selectState} />
              </SelectTrigger>
              <SelectContent>
                {states.map(state => <SelectItem key={state} value={state.toLowerCase()}>{state}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="year-select">{t.selectYear}</Label>
            <Select>
              <SelectTrigger id="year-select">
                <SelectValue placeholder={t.selectYear} />
              </SelectTrigger>
              <SelectContent>
                {years.map(year => <SelectItem key={year} value={year}>{year}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          <Button className="w-full sm:w-auto">
            <Download className="w-4 h-4 mr-2" />
            {t.downloadButton}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default DownloadDataPage;