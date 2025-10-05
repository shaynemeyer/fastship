import { useState } from 'react';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from './ui/drawer';
import { Button } from './ui/button';
import { QrReader } from 'react-qr-reader';
import { ScanQrCode } from 'lucide-react';

export default function QRScanner({
  onScan,
}: {
  onScan: (id: string) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <Drawer open={open} onDrag={() => setOpen(false)}>
      <Button variant="outline" onClick={() => setOpen(true)}>
        <ScanQrCode />
      </Button>

      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Scan Shipment Label</DrawerTitle>
        </DrawerHeader>
        {open && (
          <>
            <video id="qr-scan-video"></video>
            <QrReader
              videoId="qr-scan-video"
              onResult={(result, error) => {
                if (result) {
                  onScan(result.getText());
                  setOpen(false);
                }
              }}
              constraints={{ facingMode: 'environment' }}
            />
          </>
        )}
      </DrawerContent>
    </Drawer>
  );
}
