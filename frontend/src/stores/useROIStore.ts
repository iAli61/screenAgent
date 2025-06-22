import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface ROICoordinates {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ROISelection {
  id: string;
  name: string;
  coordinates: ROICoordinates;
  isActive: boolean;
  created: string;
  lastModified: string;
}

interface ROIState {
  // ROI data
  selections: ROISelection[];
  activeSelection: ROISelection | null;
  
  // Current editing state
  isSelecting: boolean;
  currentCoordinates: ROICoordinates | null;
  previewMode: boolean;
  
  // Monitoring state
  isMonitoring: boolean;
  lastDetectedChange: string | null;
  changeThreshold: number;
  
  // UI state
  showOverlay: boolean;
  snapToGrid: boolean;
  gridSize: number;
  
  // Actions
  setSelections: (selections: ROISelection[]) => void;
  addSelection: (selection: Omit<ROISelection, 'id' | 'created' | 'lastModified'>) => void;
  updateSelection: (id: string, updates: Partial<ROISelection>) => void;
  removeSelection: (id: string) => void;
  setActiveSelection: (selection: ROISelection | null) => void;
  
  // Editing actions
  startSelecting: () => void;
  stopSelecting: () => void;
  setCurrentCoordinates: (coordinates: ROICoordinates | null) => void;
  confirmSelection: (name: string) => void;
  
  // Monitoring actions
  startMonitoring: () => void;
  stopMonitoring: () => void;
  setChangeThreshold: (threshold: number) => void;
  recordChange: () => void;
  
  // UI actions
  toggleOverlay: () => void;
  toggleSnapToGrid: () => void;
  setGridSize: (size: number) => void;
  setPreviewMode: (enabled: boolean) => void;
  
  // Utility functions
  getSelectionById: (id: string) => ROISelection | undefined;
  getActiveCoordinates: () => ROICoordinates | null;
}

export const useROIStore = create<ROIState>()(
  devtools(
    (set, get) => ({
      // Initial state
      selections: [],
      activeSelection: null,
      isSelecting: false,
      currentCoordinates: null,
      previewMode: false,
      isMonitoring: false,
      lastDetectedChange: null,
      changeThreshold: 10,
      showOverlay: true,
      snapToGrid: false,
      gridSize: 10,

      // Actions
      setSelections: (selections) => 
        set((state) => ({ ...state, selections }), false, 'setSelections'),

      addSelection: (selectionData) => {
        const newSelection: ROISelection = {
          ...selectionData,
          id: crypto.randomUUID(),
          created: new Date().toISOString(),
          lastModified: new Date().toISOString(),
        };
        
        set((state) => ({
          ...state,
          selections: [...state.selections, newSelection],
          activeSelection: newSelection,
        }), false, 'addSelection');
      },

      updateSelection: (id, updates) => {
        set((state) => ({
          ...state,
          selections: state.selections.map(selection =>
            selection.id === id
              ? { ...selection, ...updates, lastModified: new Date().toISOString() }
              : selection
          ),
          activeSelection: state.activeSelection?.id === id
            ? { ...state.activeSelection, ...updates, lastModified: new Date().toISOString() }
            : state.activeSelection,
        }), false, 'updateSelection');
      },

      removeSelection: (id) => {
        set((state) => ({
          ...state,
          selections: state.selections.filter(selection => selection.id !== id),
          activeSelection: state.activeSelection?.id === id ? null : state.activeSelection,
        }), false, 'removeSelection');
      },

      setActiveSelection: (selection) => 
        set((state) => ({ ...state, activeSelection: selection }), false, 'setActiveSelection'),

      // Editing actions
      startSelecting: () => 
        set((state) => ({ 
          ...state, 
          isSelecting: true, 
          currentCoordinates: null 
        }), false, 'startSelecting'),

      stopSelecting: () => 
        set((state) => ({ 
          ...state, 
          isSelecting: false, 
          currentCoordinates: null 
        }), false, 'stopSelecting'),

      setCurrentCoordinates: (coordinates) => 
        set((state) => ({ ...state, currentCoordinates: coordinates }), false, 'setCurrentCoordinates'),

      confirmSelection: (name) => {
        const { currentCoordinates } = get();
        if (currentCoordinates) {
          get().addSelection({
            name,
            coordinates: currentCoordinates,
            isActive: true,
          });
          get().stopSelecting();
        }
      },

      // Monitoring actions
      startMonitoring: () => 
        set((state) => ({ ...state, isMonitoring: true }), false, 'startMonitoring'),

      stopMonitoring: () => 
        set((state) => ({ ...state, isMonitoring: false }), false, 'stopMonitoring'),

      setChangeThreshold: (changeThreshold) => 
        set((state) => ({ ...state, changeThreshold }), false, 'setChangeThreshold'),

      recordChange: () => 
        set((state) => ({ 
          ...state, 
          lastDetectedChange: new Date().toISOString() 
        }), false, 'recordChange'),

      // UI actions
      toggleOverlay: () => 
        set((state) => ({ ...state, showOverlay: !state.showOverlay }), false, 'toggleOverlay'),

      toggleSnapToGrid: () => 
        set((state) => ({ ...state, snapToGrid: !state.snapToGrid }), false, 'toggleSnapToGrid'),

      setGridSize: (gridSize) => 
        set((state) => ({ ...state, gridSize }), false, 'setGridSize'),

      setPreviewMode: (previewMode) => 
        set((state) => ({ ...state, previewMode }), false, 'setPreviewMode'),

      // Utility functions
      getSelectionById: (id) => {
        return get().selections.find(selection => selection.id === id);
      },

      getActiveCoordinates: () => {
        const { activeSelection, currentCoordinates, isSelecting } = get();
        
        if (isSelecting && currentCoordinates) {
          return currentCoordinates;
        }
        
        if (activeSelection) {
          return activeSelection.coordinates;
        }
        
        return null;
      },
    }),
    {
      name: 'roi-store',
    }
  )
);
