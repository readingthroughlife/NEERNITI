import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/Label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import { Checkbox } from '../ui/Checkbox';
import { Eye, EyeOff } from 'lucide-react';
import Logo from '../Logo';
import { signInWithGoogle, signInWithEmail } from '../../utils/firebase';
import { toast } from 'sonner';

const LoginPage = ({ onLogin }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (email && password) {
        const user = await signInWithEmail(email, password);
        if (user) {
          toast.success("Logged in successfully!");
          onLogin({
            name: user.displayName || email.split('@')[0],
            email: user.email,
            uid: user.uid,
          });
        }
      }
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleGuestLogin = () => {
    onLogin({ 
      name: 'Guest', 
      email: 'guest@neerniti.io', 
      role: 'General User', 
      isGuest: true 
    });
  };

  const handleGoogleSignIn = async () => {
    try {
      const user = await signInWithGoogle();
      if (user) {
        toast.success("Logged in with Google!");
        onLogin({
          name: user.displayName,
          email: user.email,
          uid: user.uid,
        });
      }
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <div className="min-h-screen bg-muted/40 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader className="text-center p-6">
            <div className="mx-auto mb-4"><Logo /></div>
            <CardTitle>Welcome to NeerNiti</CardTitle>
            <CardDescription>Sign in to access your dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="any@email.com" required onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input id="password" type={showPassword ? "text" : "password"} placeholder="any password" required onChange={(e) => setPassword(e.target.value)} />
                  <Button type="button" variant="ghost" size="icon" className="absolute right-1 top-1 h-8 w-8" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="remember-me" />
                <Label htmlFor="remember-me" className="font-normal">Remember me</Label>
              </div>
              <Button type="submit" className="w-full">Sign In</Button>
            </form>
            <div className="mt-6 relative">
              <div className="absolute inset-0 flex items-center"><span className="w-full border-t" /></div>
              <div className="relative flex justify-center text-xs uppercase"><span className="bg-card px-2 text-muted-foreground">Or</span></div>
            </div>
            <Button variant="outline" className="w-full mt-6" onClick={handleGuestLogin}>Continue as Guest</Button>
            <Button variant="outline" className="w-full mt-2" onClick={handleGoogleSignIn}>Sign In with Google</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;