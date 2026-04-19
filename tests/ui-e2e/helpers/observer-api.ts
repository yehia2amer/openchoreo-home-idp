import { OBSERVER_URL } from "../playwright.config.js";
import { getAuthToken } from "./auth-token.js";

// ---------------------------------------------------------------------------
// Search Scopes
// ---------------------------------------------------------------------------

export interface ComponentSearchScope {
  namespace: string;
  project?: string;
  component?: string;
  environment?: string;
}

export interface WorkflowSearchScope {
  namespace: string;
  workflowName: string;
  workflowRunId?: string;
  workflowRunRetryId?: string;
  nodeName?: string;
}

// ---------------------------------------------------------------------------
// Logs
// ---------------------------------------------------------------------------

export interface LogsQueryRequest {
  startTime: string;
  endTime: string;
  limit?: number;
  sortOrder?: "asc" | "desc";
  searchScope: ComponentSearchScope | WorkflowSearchScope;
  logLevels?: Array<"DEBUG" | "INFO" | "WARN" | "ERROR">;
  searchPhrase?: string;
}

export interface ComponentLogEntry {
  timestamp: string;
  log: string;
  level: string;
  metadata: {
    componentName?: string;
    projectName?: string;
    environmentName?: string;
    namespaceName?: string;
    componentUid?: string;
    projectUid?: string;
    environmentUid?: string;
    containerName?: string;
    podName?: string;
    podNamespace?: string;
  };
}

export interface LogsQueryResponse {
  logs: ComponentLogEntry[];
  total: number;
  tookMs: number;
}

// ---------------------------------------------------------------------------
// Metrics
// ---------------------------------------------------------------------------

export interface MetricsQueryRequest {
  metric: "resource" | "http";
  startTime: string;
  endTime: string;
  step?: string;
  searchScope: ComponentSearchScope;
}

export interface MetricsTimeSeriesItem {
  timestamp: string;
  value: number;
}

export interface ResourceMetricsTimeSeries {
  cpuUsage?: MetricsTimeSeriesItem[];
  cpuRequests?: MetricsTimeSeriesItem[];
  cpuLimits?: MetricsTimeSeriesItem[];
  memoryUsage?: MetricsTimeSeriesItem[];
  memoryRequests?: MetricsTimeSeriesItem[];
  memoryLimits?: MetricsTimeSeriesItem[];
}

export interface HttpMetricsTimeSeries {
  requestCount?: MetricsTimeSeriesItem[];
  successfulRequestCount?: MetricsTimeSeriesItem[];
  unsuccessfulRequestCount?: MetricsTimeSeriesItem[];
  meanLatency?: MetricsTimeSeriesItem[];
  latencyP50?: MetricsTimeSeriesItem[];
  latencyP90?: MetricsTimeSeriesItem[];
  latencyP99?: MetricsTimeSeriesItem[];
}

// ---------------------------------------------------------------------------
// Traces
// ---------------------------------------------------------------------------

export interface TracesQueryRequest {
  startTime: string;
  endTime: string;
  limit?: number;
  sortOrder?: "asc" | "desc";
  searchScope: ComponentSearchScope;
}

export interface TraceItem {
  traceId: string;
  traceName?: string;
  spanCount?: number;
  rootSpanId?: string;
  rootSpanName?: string;
  rootSpanKind?: string;
  startTime?: string;
  endTime?: string;
  durationNs?: number;
  hasErrors?: boolean;
}

export interface TracesQueryResponse {
  traces: TraceItem[];
  total: number;
  tookMs: number;
}

export interface SpanItem {
  spanId: string;
  spanName: string;
  spanKind: string;
  startTime: string;
  endTime: string;
  durationNs: number;
  parentSpanId?: string;
  status: "ok" | "error" | "unset";
}

export interface TraceSpansQueryResponse {
  spans: SpanItem[];
  total: number;
  tookMs: number;
}

export interface SpanAttribute {
  key: string;
  value: string;
}

export interface TraceSpanDetailsResponse {
  spanId: string;
  spanName: string;
  spanKind: string;
  startTime: string;
  endTime: string;
  durationNs: number;
  parentSpanId?: string;
  status: "ok" | "error" | "unset";
  attributes: SpanAttribute[];
}

// ---------------------------------------------------------------------------
// Alert Rules
// ---------------------------------------------------------------------------

export interface AlertRuleRequest {
  metadata: {
    name: string;
    namespace: string;
    projectUid: string;
    environmentUid: string;
    componentUid: string;
  };
  source: {
    type: "log" | "metric";
    query?: string;
    metric?: string;
  };
  condition: {
    enabled: boolean;
    window: string;
    interval: string;
    operator: "gt" | "gte" | "lt" | "lte" | "eq" | "neq";
    threshold: number;
  };
}

export interface AlertRuleResponse {
  metadata: AlertRuleRequest["metadata"];
  source: AlertRuleRequest["source"];
  condition: AlertRuleRequest["condition"];
}

export interface AlertingRuleSyncResponse {
  action: "created" | "updated" | "unchanged" | "deleted";
  lastSyncedAt?: string;
  status: "synced" | "failed";
  ruleLogicalId?: string;
  ruleBackendId?: string;
}

// ---------------------------------------------------------------------------
// Alert Webhook
// ---------------------------------------------------------------------------

export interface AlertWebhookRequest {
  ruleName: string;
  ruleNamespace: string;
  alertValue?: number;
  alertTimestamp?: string;
}

export interface AlertWebhookResponse {
  message?: string;
  status?: "success" | "error";
}

// ---------------------------------------------------------------------------
// Alerts Query
// ---------------------------------------------------------------------------

export interface AlertsQueryRequest {
  startTime: string;
  endTime: string;
  limit?: number;
  sortOrder?: "asc" | "desc";
  searchScope: ComponentSearchScope;
}

export interface AlertsQueryResponse {
  alerts: Array<{
    timestamp: string;
    alertId: string;
    alertValue?: string;
    notificationChannels?: string[];
    incidentEnabled?: boolean;
    metadata?: {
      alertRule?: {
        name?: string;
        description?: string;
        severity?: "info" | "warning" | "critical";
        source?: { type?: string; query?: string; metric?: string };
        condition?: {
          operator?: string;
          threshold?: number;
          window?: string;
          interval?: string;
        };
      };
      labels?: {
        componentName?: string;
        environmentName?: string;
        projectName?: string;
        namespaceName?: string;
        componentUid?: string;
        environmentUid?: string;
        projectUid?: string;
      };
    };
  }>;
  total: number;
  tookMs: number;
}

// ---------------------------------------------------------------------------
// Incidents
// ---------------------------------------------------------------------------

export interface IncidentsQueryRequest {
  startTime: string;
  endTime: string;
  limit?: number;
  sortOrder?: "asc" | "desc";
  searchScope: ComponentSearchScope;
}

export interface IncidentsQueryResponse {
  incidents: Array<{
    timestamp: string;
    alertId: string;
    incidentId: string;
    incidentTriggerAiRca?: boolean;
    status: "active" | "acknowledged" | "resolved";
    triggeredAt: string;
    acknowledgedAt?: string;
    resolvedAt?: string;
    notes?: string;
    description?: string;
    labels?: {
      componentName?: string;
      environmentName?: string;
      projectName?: string;
      namespaceName?: string;
      componentUid?: string;
      environmentUid?: string;
      projectUid?: string;
    };
  }>;
  total: number;
  tookMs: number;
}

export interface IncidentPutRequest {
  status: "active" | "acknowledged" | "resolved";
  notes?: string;
  description?: string;
}

export interface IncidentPutResponse {
  incidentId: string;
  alertId?: string;
  status: "active" | "acknowledged" | "resolved";
  triggeredAt?: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  notes?: string;
  description?: string;
  incidentTriggerAiRca?: boolean;
  labels?: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Error
// ---------------------------------------------------------------------------

export interface ErrorResponse {
  title: string;
  errorCode?: string;
  message?: string;
}

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export class ObserverApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? OBSERVER_URL;
  }

  private getAuthHeaders(): Record<string, string> {
    const token = getAuthToken();
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  private getPublicHeaders(): Record<string, string> {
    return { "Content-Type": "application/json" };
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    auth = true,
  ): Promise<{ status: number; body: T }> {
    const url = `${this.baseUrl}${path}`;
    const headers = auth ? this.getAuthHeaders() : this.getPublicHeaders();
    const options: RequestInit = {
      method,
      headers,
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    };

    const response = await fetch(url, options);
    const text = await response.text();
    let parsed: T;
    try {
      parsed = JSON.parse(text) as T;
    } catch {
      parsed = text as unknown as T;
    }
    return { status: response.status, body: parsed };
  }

  // --- Health (public) ---
  async health() {
    return this.request<{ status: string }>("GET", "/health", undefined, false);
  }

  // --- Logs ---
  async queryLogs(req: LogsQueryRequest) {
    return this.request<LogsQueryResponse>("POST", "/api/v1/logs/query", req);
  }

  // --- Metrics ---
  async queryMetrics(req: MetricsQueryRequest) {
    return this.request<ResourceMetricsTimeSeries | HttpMetricsTimeSeries>(
      "POST",
      "/api/v1/metrics/query",
      req,
    );
  }

  // --- Traces ---
  async queryTraces(req: TracesQueryRequest) {
    return this.request<TracesQueryResponse>(
      "POST",
      "/api/v1alpha1/traces/query",
      req,
    );
  }

  async queryTraceSpans(traceId: string, req: TracesQueryRequest) {
    return this.request<TraceSpansQueryResponse>(
      "POST",
      `/api/v1alpha1/traces/${traceId}/spans/query`,
      req,
    );
  }

  async getSpanDetails(traceId: string, spanId: string) {
    return this.request<TraceSpanDetailsResponse>(
      "GET",
      `/api/v1alpha1/traces/${traceId}/spans/${spanId}`,
    );
  }

  // --- Alert Rules ---
  async createAlertRule(
    sourceType: "log" | "metric",
    req: AlertRuleRequest,
  ) {
    return this.request<AlertingRuleSyncResponse>(
      "POST",
      `/api/v1alpha1/alerts/sources/${sourceType}/rules`,
      req,
    );
  }

  async getAlertRule(sourceType: "log" | "metric", ruleName: string) {
    return this.request<AlertRuleResponse>(
      "GET",
      `/api/v1alpha1/alerts/sources/${sourceType}/rules/${ruleName}`,
    );
  }

  async updateAlertRule(
    sourceType: "log" | "metric",
    ruleName: string,
    req: AlertRuleRequest,
  ) {
    return this.request<AlertingRuleSyncResponse>(
      "PUT",
      `/api/v1alpha1/alerts/sources/${sourceType}/rules/${ruleName}`,
      req,
    );
  }

  async deleteAlertRule(sourceType: "log" | "metric", ruleName: string) {
    return this.request<AlertingRuleSyncResponse>(
      "DELETE",
      `/api/v1alpha1/alerts/sources/${sourceType}/rules/${ruleName}`,
    );
  }

  // --- Alert Webhook (public) ---
  async sendAlertWebhook(req: AlertWebhookRequest) {
    return this.request<AlertWebhookResponse>(
      "POST",
      "/api/v1alpha1/alerts/webhook",
      req,
      false,
    );
  }

  // --- Alerts Query ---
  async queryAlerts(req: AlertsQueryRequest) {
    return this.request<AlertsQueryResponse>(
      "POST",
      "/api/v1alpha1/alerts/query",
      req,
    );
  }

  // --- Incidents ---
  async queryIncidents(req: IncidentsQueryRequest) {
    return this.request<IncidentsQueryResponse>(
      "POST",
      "/api/v1alpha1/incidents/query",
      req,
    );
  }

  async updateIncident(incidentId: string, req: IncidentPutRequest) {
    return this.request<IncidentPutResponse>(
      "PUT",
      `/api/v1alpha1/incidents/${incidentId}`,
      req,
    );
  }

  // --- Raw request (for auth failure tests) ---
  async rawRequest(
    method: string,
    path: string,
    body?: unknown,
    headers?: Record<string, string>,
  ) {
    const url = `${this.baseUrl}${path}`;
    const options: RequestInit = {
      method,
      headers: headers ?? {},
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    };
    const response = await fetch(url, options);
    const text = await response.text();
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
    return { status: response.status, body: parsed };
  }
}
