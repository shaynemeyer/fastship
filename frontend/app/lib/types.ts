import type { TagName, ShipmentEvent } from './client';

/** TagRead */
export interface TagRead {
  name: TagName;
  /** Instruction */
  instruction: string;
}

/** Shipment */
export interface Shipment {
  /**
   * Content
   * @maxLength 100
   */
  content: string;
  /**
   * Weight
   * @max 25
   */
  weight: number;
  /**
   * Destination
   * location zipcode
   */
  destination: number;
  /**
   * Id
   * @format uuid
   */
  id: string;
  /** Timeline */
  timeline: ShipmentEvent[];
  /**
   * Estimated Delivery
   * @format date-time
   */
  estimated_delivery: string;
  /** Tags */
  tags: TagRead[];
}
