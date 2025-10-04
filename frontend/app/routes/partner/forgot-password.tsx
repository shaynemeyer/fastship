import { ForgotPasswordForm } from '~/components/forgot-password-form';

export default function DeliveryPartnerForgotPasswordPage() {
  return (
    <div className="bg-muted flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <ForgotPasswordForm user="partner" />
      </div>
    </div>
  );
}
