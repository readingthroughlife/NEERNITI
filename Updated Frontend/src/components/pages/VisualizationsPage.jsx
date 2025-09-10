import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import { Button } from '../ui/Button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Download, TrendingUp, TrendingDown, Activity } from 'lucide-react';

const StatCard = ({ title, value, change, trend, icon: Icon }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      <p className="text-xs text-muted-foreground flex items-center gap-1">
        {trend === 'up' ? <TrendingUp className="h-3 w-3 text-green-500" /> : <TrendingDown className="h-3 w-3 text-red-500" />}
        {change} from last month
      </p>
    </CardContent>
  </Card>
);

const VisualizationsPage = () => {
  const lineChartData = [
    { year: '2019', level: 15.2 }, { year: '2020', level: 14.8 },
    { year: '2021', level: 13.5 }, { year: '2022', level: 12.9 },
    { year: '2023', level: 12.1 }, { year: '2024', level: 11.8 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Groundwater Visualizations</h1>
          <p className="text-muted-foreground">Comprehensive analysis and trends for general user</p>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="all"><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">All Regions</SelectItem></SelectContent></Select>
          <Select defaultValue="5years"><SelectTrigger className="w-32"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="5years">5 Years</SelectItem></SelectContent></Select>
          <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export</Button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Average Water Level" value="12.3m" change="-2.1%" trend="down" icon={Activity} />
        <StatCard title="Critical Areas" value="23" change="+3" trend="up" icon={TrendingUp} />
        <StatCard title="Total Wells Monitored" value="1,247" change="+45" trend="up" icon={TrendingUp} />
        <StatCard title="Quality Score" value="6.8/10" change="+0.2" trend="up" icon={TrendingUp} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Water Level Trends (2019-2024)</CardTitle>
          <CardDescription>This is static placeholder data. The visuals will be derived from backend data later.</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={lineChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="level" stroke="hsl(var(--primary))" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default VisualizationsPage;