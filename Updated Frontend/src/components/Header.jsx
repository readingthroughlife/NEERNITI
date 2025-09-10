import React from 'react';
import { useTheme } from './ThemeContext';
import { Button } from './ui/Button';
import { Avatar, AvatarFallback } from './ui/Avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/DropdownMenu';
import { Badge } from './ui/Badge';
import { Menu, Sun, Moon, LogOut, Globe, User as UserIcon } from 'lucide-react';
import Logo from './Logo';
import { translations } from './i18n';

const Header = ({ user, onLogout, setSidebarOpen, language, setLanguage }) => {
  const { theme, toggleTheme } = useTheme();
  const t = translations[language];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' },
  ];

  return (
    <header className="bg-card border-b px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(prev => !prev)}>
          <Menu className="h-5 w-5" />
        </Button>
        <Logo />
      </div>

      <div className="flex items-center gap-2">
        <Badge variant="secondary" className="hidden sm:inline-flex">
          {user.isGuest ? t.guestMode : user.role}
        </Badge>
        <span className="hidden md:inline text-sm text-muted-foreground">
          {t.welcomeUser}, {user.name}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-1">
              <Globe className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            {languages.map((lang) => (
              <DropdownMenuItem key={lang.code} onClick={() => setLanguage(lang.code)}>
                {lang.name}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant="ghost" size="icon" className="h-9 w-9" onClick={toggleTheme}>
          {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-9 w-9 rounded-full">
              <Avatar className="h-9 w-9">
                <AvatarFallback>{user.name ? user.name.charAt(0).toUpperCase() : 'U'}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <UserIcon className="mr-2 h-4 w-4" /> {t.profile}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onLogout}>
              <LogOut className="mr-2 h-4 w-4" /> {t.logout}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default Header;