export type Uuid = string;
export type IsoDateTime = string;

export type CollectionPage<T> = {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
};

export type ListQueryParams = {
  search?: string | null;
  page?: number;
  size?: number;
};

export type Customer = {
  id: Uuid;
  name: string;
  contactPersonName: string | null;
  contactPersonPhone: string | null;
  email: string;
  notificationsEnabled: boolean;
  gemFuryUsed: boolean;
  customerSymbol: string;
  createdAt: IsoDateTime;
  modifiedAt: IsoDateTime;
};

export type CustomerCreateInput = {
  name: string;
  email: string;
  customerSymbol: string;
  notificationsEnabled?: boolean;
  gemFuryUsed?: boolean;
  contactPersonName?: string | null;
  contactPersonPhone?: string | null;
};

export type CustomerUpdateInput = {
  name?: string | null;
  email?: string | null;
  customerSymbol?: string | null;
  notificationsEnabled?: boolean | null;
  gemFuryUsed?: boolean | null;
  contactPersonName?: string | null;
  contactPersonPhone?: string | null;
};

export type Product = {
  id: Uuid;
  name: string;
  kind: string;
  createdAt: IsoDateTime;
  modifiedAt: IsoDateTime;
};

export type ProductCreateInput = {
  name: string;
  kind: string;
};

export type ProductUpdateInput = {
  name?: string | null;
  kind?: string | null;
};

export type Kind = {
  id: Uuid;
  name: string;
  createdAt: IsoDateTime;
  modifiedAt: IsoDateTime;
};

export type KindCreateInput = {
  name: string;
};

export type KindUpdateInput = {
  name?: string | null;
};

export type License = {
  id: Uuid;
  customerId: Uuid | null;
  productId: Uuid | null;
  kindId: Uuid | null;
  licenseCount: number;
  licenseState: string;
  licenseKey: string;
  licenseEmail: string;
  doubleSend: boolean;
  beginDate: IsoDateTime;
  endDate: IsoDateTime;
  notificationDate: IsoDateTime;
  createdAt: IsoDateTime;
  modifiedAt: IsoDateTime;
};

export type LicenseCreateInput = {
  customerId?: Uuid | null;
  productId?: Uuid | null;
  kindId?: Uuid | null;
  licenseCount: number;
  licenseState: string;
  licenseKey: string;
  licenseEmail: string;
  doubleSend?: boolean;
  beginDate: IsoDateTime;
  endDate: IsoDateTime;
  notificationDate: IsoDateTime;
};

export type LicenseUpdateInput = {
  customerId?: Uuid | null;
  productId?: Uuid | null;
  kindId?: Uuid | null;
  licenseCount?: number | null;
  licenseState?: string | null;
  licenseKey?: string | null;
  licenseEmail?: string | null;
  doubleSend?: boolean | null;
  beginDate?: IsoDateTime | null;
  endDate?: IsoDateTime | null;
  notificationDate?: IsoDateTime | null;
};

export type LicenseGenerateInput = {
  customerSymbol?: string;
  endDate?: IsoDateTime;
  licenseCount?: number;
};

export type LicenseGeneratedKey = {
  licenseKey: string;
};

export type AppPackage = {
  id: Uuid;
  versionNumber: string;
  binaryName: string;
  gemFuryUrl: string;
  binaryUrl: string;
  createdAt: IsoDateTime;
  modifiedAt: IsoDateTime;
};

export type AppPackageCreateInput = {
  versionNumber: string;
  binaryName: string;
  gemFuryUrl: string;
  binaryUrl: string;
};

export type AppPackageUpdateInput = {
  versionNumber?: string | null;
  binaryName?: string | null;
  gemFuryUrl?: string | null;
  binaryUrl?: string | null;
};

export type SmtpCredential = {
  secretName: string;
  secretVersion: string | null;
  host: string;
  port: number;
  username: string;
  senderEmail: string | null;
  useTls: boolean;
  useSsl: boolean;
  createdAt: IsoDateTime;
  modifiedAt: IsoDateTime;
};

export type SmtpCredentialCreateInput = {
  host: string;
  port: number;
  username: string;
  password: string;
  senderEmail?: string | null;
  useTls?: boolean;
  useSsl?: boolean;
};

export type SmtpCredentialUpdateInput = {
  host?: string | null;
  port?: number | null;
  username?: string | null;
  password?: string | null;
  senderEmail?: string | null;
  useTls?: boolean | null;
  useSsl?: boolean | null;
};

export type AuditLogEntry = {
  id: Uuid;
  actorId: string | null;
  actorType: string;
  actorDisplayName: string | null;
  source: string;
  requestId: string | null;
  action: string;
  entityType: string;
  entityId: string;
  summary: string | null;
  diff: Record<string, unknown>[] | Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  occurredAt: IsoDateTime;
  recordedAt: IsoDateTime;
};

export type AuditLogListQuery = ListQueryParams & {
  entityType?: string | null;
  entityId?: string | null;
  requestId?: string | null;
  actorId?: string | null;
  source?: string | null;
  occurredFrom?: IsoDateTime | null;
  occurredTo?: IsoDateTime | null;
};

export type HealthServices = {
  postgres: "ok" | "error";
  keyVault: "ok" | "error";
};

export type HealthResponse = {
  status: "ok" | "degraded";
  services: HealthServices;
  errors?: Record<string, string>;
};
