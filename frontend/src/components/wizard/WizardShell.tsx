import { useDesignStore } from '../../store/designStore';
import { StepBar } from './StepBar';
import { Step1BoxAndComponents } from './steps/Step1BoxAndComponents';
import { Step2SortAndPlan } from './steps/Step2SortAndPlan';
import { Step3LayoutEditor } from './steps/Step3LayoutEditor';
import { Step4PreviewAndExport } from './steps/Step4PreviewAndExport';

interface Props {
  onOpenSettings: () => void;
}

export function WizardShell({ onOpenSettings }: Props) {
  const currentStep = useDesignStore((state) => state.currentStep);

  const steps = [
    { id: 1, name: 'Box & Components' },
    { id: 2, name: 'Sort & Plan' },
    { id: 3, name: 'Layout Editor' },
    { id: 4, name: 'Preview & Export' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <StepBar steps={steps} currentStep={currentStep} />
      <div className="max-w-7xl mx-auto px-4 py-8">
        {currentStep === 1 && <Step1BoxAndComponents onOpenSettings={onOpenSettings} />}
        {currentStep === 2 && <Step2SortAndPlan />}
        {currentStep === 3 && <Step3LayoutEditor />}
        {currentStep === 4 && <Step4PreviewAndExport />}
      </div>
    </div>
  );
}
