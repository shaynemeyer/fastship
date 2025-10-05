import { useQuery } from '@tanstack/react-query';
import { useContext } from 'react';
import { Navigate } from 'react-router';
import { AppSidebar } from '~/components/app-sidebar';
import NumberLabel from '~/components/labels/number-label';
import Loading from '~/components/loading';
import ShipmentCard from '~/components/shipment/shimpment-card';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '~/components/ui/breadcrumb';
import { Separator } from '~/components/ui/separator';
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '~/components/ui/sidebar';
import { AuthContext } from '~/contexts/AuthContext';
import api from '~/lib/api';
import { ShipmentStatus } from '~/lib/client';
import type { Shipment } from '~/lib/types';
import { getShipmentsCountForStatus } from '~/lib/utils';

export default function DashboardPage() {
  const { token, user } = useContext(AuthContext);

  if (!token) {
    return <Navigate to={`/`} />;
  }

  const { data, isLoading, isError } = useQuery({
    queryKey: ['shipments'],
    queryFn: async () => {
      const userApi = user === 'seller' ? api.seller : api.partner;
      const { data } = await userApi.getShipments({ token });
      return data;
    },
  });

  if (isError) {
    return (
      <div className="flex h-screen items-center justify-center">
        <h1 className="text-2xl font-bold">Error loading shipments</h1>
      </div>
    );
  }

  return (
    <SidebarProvider
      style={
        {
          '--sidebar-width': '19rem',
        } as React.CSSProperties
      }
    >
      <AppSidebar currentRoute="Dashboard" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator
            orientation="vertical"
            className="mr-2 data-[orientation=vertical]:h-4"
          />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="#">
                  Building Your Application
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator className="hidden md:block" />
              <BreadcrumbItem>
                <BreadcrumbPage>Data Fetching</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {isLoading || !data ? (
            <Loading />
          ) : (
            <>
              <div className="grid auto-rows-min gap-4 md:grid-cols-4">
                <NumberLabel value={data.length} label="Total Shipments" />
                <NumberLabel
                  value={getShipmentsCountForStatus(
                    data,
                    ShipmentStatus.Placed
                  )}
                  label="Placed"
                />
                <NumberLabel
                  value={getShipmentsCountForStatus(
                    data,
                    ShipmentStatus.InTransit
                  )}
                  label="In Transit"
                />
                <NumberLabel
                  value={getShipmentsCountForStatus(
                    data,
                    ShipmentStatus.Delivered
                  )}
                  label="Delivered"
                />
              </div>
              <div className="grid auto-rows-min gap-4 md:grid-cols-4">
                {data.map((shipment: Shipment) => (
                  <ShipmentCard shipment={shipment} />
                ))}
              </div>
            </>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
