import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/Dialog';
import { RadioGroup, RadioGroupItem } from './ui/RadioGroup';
import { Label } from './ui/Label';
import { Button } from './ui/Button';
import { User, FlaskConical, Map, Leaf } from 'lucide-react';

const roles = [
  { id: 'General User', name: 'General User', icon: User },
  { id: 'Researcher', name: 'Researcher', icon: FlaskConical },
  { id: 'Planner', name: 'Planner', icon: Map },
  { id: 'Farmer', name: 'Farmer', icon: Leaf },
];

const RoleSelectionModal = ({ isOpen, onRoleSelect }) => {
  const [selectedRole, setSelectedRole] = useState('');

  return (
    <Dialog open={isOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Choose Your Role</DialogTitle>
          <DialogDescription>
            Select a role to tailor your experience.
          </DialogDescription>
        </DialogHeader>
        <RadioGroup value={selectedRole} onValueChange={setSelectedRole} className="space-y-2 py-4">
          {roles.map((role) => (
            <Label key={role.id} htmlFor={role.id} className="flex items-center p-4 border rounded-md cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
              <role.icon className="h-5 w-5 mr-3" />
              {/* This span renders the role name */}
              <span className="flex-1">{role.name}</span>
              <RadioGroupItem value={role.id} id={role.id} />
            </Label>
          ))}
        </RadioGroup>
        <Button onClick={() => onRoleSelect(selectedRole)} disabled={!selectedRole} className="w-full">
          Continue
        </Button>
      </DialogContent>
    </Dialog>
  );
};

export default RoleSelectionModal;