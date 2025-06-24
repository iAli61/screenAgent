import { createContext, useContext, useState, ReactNode } from 'react';

interface ROI {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ROIContextType {
  selectedROI: ROI | null;
  setSelectedROI: (roi: ROI | null) => void;
}

const ROIContext = createContext<ROIContextType | undefined>(undefined);

export function ROIProvider({ children }: { children: ReactNode }) {
  const [selectedROI, setSelectedROI] = useState<ROI | null>(null);

  return (
    <ROIContext.Provider value={{ selectedROI, setSelectedROI }}>
      {children}
    </ROIContext.Provider>
  );
}

export function useROI() {
  const context = useContext(ROIContext);
  if (context === undefined) {
    throw new Error('useROI must be used within a ROIProvider');
  }
  return context;
}
