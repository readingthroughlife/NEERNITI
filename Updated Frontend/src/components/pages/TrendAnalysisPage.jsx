import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FileText, BarChart2, TrendingUp } from 'lucide-react';
import { translations } from '../i18n';

const StatCard = ({ title, value, icon: Icon }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
    </CardContent>
  </Card>
);

const TrendAnalysisPage = ({ language }) => {
  const t = translations[language];
  const chartData = [
    { year: '2020', value: 2400 },
    { year: '2021', value: 1398 },
    { year: '2022', value: 9800 },
    { year: '2023', value: 3908 },
    { year: '2024', value: 4800 },
  ];

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">{t.trendAnalysisTitle}</h1>
        <p className="text-muted-foreground">{t.trendAnalysisDescription}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title={t.totalRecords} value="1.2M" icon={FileText} />
        <StatCard title={t.dataGrowth} value="+15%" icon={TrendingUp} />
        <StatCard title={t.reportsGenerated} value="5,231" icon={BarChart2} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t.yearlyTrends}</CardTitle>
          <CardDescription>This is a sample chart with static data for demonstration.</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" stroke="#888888" fontSize={12} />
              <YAxis stroke="#888888" fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrendAnalysisPage;