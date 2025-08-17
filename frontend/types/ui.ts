import { ReactNode } from 'react';

// Common UI component props
export interface BaseComponentProps {
  className?: string;
  children?: ReactNode;
}

// Loading state props
export interface LoadingProps extends BaseComponentProps {
  isLoading: boolean;
  loadingText?: string;
}

// Modal/Dialog props
export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
}

// Form component props
export interface FormFieldProps extends BaseComponentProps {
  label: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}

// Card component variants
export type CardVariant = 'default' | 'interactive' | 'selected' | 'disabled';

// Button variants and sizes
export type ButtonVariant = 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
export type ButtonSize = 'default' | 'sm' | 'lg' | 'icon';

// Animation states
export type AnimationState = 'idle' | 'loading' | 'success' | 'error';

// Theme modes
export type ThemeMode = 'light' | 'dark' | 'system';

// Screen sizes for responsive design
export type ScreenSize = 'mobile' | 'tablet' | 'desktop' | 'wide';

// Game UI specific types
export interface GameUIState {
  sidebarOpen: boolean;
  theme: ThemeMode;
  fontSize: 'small' | 'medium' | 'large';
  animationsEnabled: boolean;
}

export interface ChoiceButtonProps extends BaseComponentProps {
  choice: string;
  index: number;
  selected?: boolean;
  disabled?: boolean;
  onClick: (choice: string, index: number) => void;
}

export interface MessageBubbleProps extends BaseComponentProps {
  message: import('./game').GameMessage;
  isTyping?: boolean;
  showAvatar?: boolean;
}
