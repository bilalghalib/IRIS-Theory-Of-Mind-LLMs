/**
 * Aperture TypeScript SDK
 *
 * Official TypeScript/JavaScript client for the Aperture API.
 *
 * @example
 * ```typescript
 * import { Aperture } from '@aperture/sdk';
 *
 * const client = new Aperture({ apiKey: 'your-key' });
 *
 * const response = await client.sendMessage({
 *   userId: 'user_123',
 *   message: 'Hello!',
 *   llmProvider: 'openai',
 *   llmApiKey: 'sk-...'
 * });
 * ```
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// ==================== Types ====================

export interface ApertureConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export interface SendMessageParams {
  userId: string;
  message: string;
  llmProvider: 'openai' | 'anthropic';
  llmApiKey: string;
  conversationId?: string;
  llmModel?: string;
  systemPrompt?: string;
  temperature?: number;
  maxTokens?: number;
  metadata?: Record<string, any>;
}

export interface MessageResponse {
  conversationId: string;
  messageId: string;
  response: string;
  apertureLink: string;
  assessmentCount: number;
  provider: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

export interface Assessment {
  id: string;
  userId: string;
  element: string;
  valueType: 'score' | 'tag' | 'range' | 'text';
  valueData: any;
  value: any;
  reasoning: string;
  confidence: number;
  createdAt: string;
  updatedAt: string;
  userCorrected?: boolean;
  observationCount?: number;
}

export interface AssessmentWithEvidence extends Assessment {
  evidence: Array<{
    userMessage: string;
    timestamp: string;
    conversationId: string;
  }>;
}

export interface GetAssessmentsParams {
  element?: string;
  minConfidence?: number;
  maxConfidence?: number;
  limit?: number;
}

export interface DiscoverPatternsParams {
  minUsers?: number;
  minOccurrenceRate?: number;
  lookbackDays?: number;
}

export interface DiscoveredPattern {
  name: string;
  description: string;
  detectedIn: number;
  occurrenceRate: number;
  confidence: number;
  suggestedConstruct: any;
  evidence: string[];
}

export interface ConstructFromDescriptionResult {
  matchType: 'template' | 'custom';
  suggestedTemplates?: Array<{
    id: string;
    name: string;
    description: string;
    similarity: number;
    config: any;
  }>;
  customGenerated?: any;
}

export interface ConstructTemplate {
  id: string;
  name: string;
  description: string;
  useCase: string;
  config: any;
}

export interface UserCorrection {
  correctionType: 'wrong_value' | 'wrong_interpretation' | 'not_applicable' | 'other';
  correctedValue?: any;
  userExplanation?: string;
}

// ==================== Errors ====================

export class ApertureError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApertureError';
  }
}

export class ApertureAPIError extends ApertureError {
  statusCode: number;

  constructor(statusCode: number, message: string) {
    super(`API Error ${statusCode}: ${message}`);
    this.statusCode = statusCode;
    this.name = 'ApertureAPIError';
  }
}

// ==================== Main Client ====================

/**
 * Aperture API Client
 *
 * @example
 * ```typescript
 * const client = new Aperture({
 *   apiKey: 'aperture_xxx',
 *   baseUrl: 'https://api.aperture.dev',
 *   timeout: 30000
 * });
 *
 * const response = await client.sendMessage({
 *   userId: 'user_123',
 *   message: "I'm deploying on AWS",
 *   llmProvider: 'openai',
 *   llmApiKey: 'sk-...'
 * });
 *
 * console.log(response.response);
 * console.log(response.apertureLink);
 * ```
 */
export class Aperture {
  private client: AxiosInstance;

  constructor(config: ApertureConfig) {
    const baseURL = config.baseUrl || 'https://api.aperture.dev';
    const timeout = config.timeout || 30000;

    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'X-Aperture-API-Key': config.apiKey,
        'Content-Type': 'application/json',
        'User-Agent': '@aperture/sdk/0.1.0'
      }
    });

    // Error interceptor
    this.client.interceptors.response.use(
      response => response,
      (error: AxiosError) => {
        if (error.response) {
          const detail = (error.response.data as any)?.detail || 'Unknown error';
          throw new ApertureAPIError(error.response.status, detail);
        }
        throw new ApertureError(`Request failed: ${error.message}`);
      }
    );
  }

  // ==================== Messages ====================

  /**
   * Send a message through Aperture
   *
   * @param params - Message parameters
   * @returns Message response with AI reply and metadata
   *
   * @example
   * ```typescript
   * const response = await client.sendMessage({
   *   userId: 'user_123',
   *   message: 'Help me deploy to AWS',
   *   llmProvider: 'openai',
   *   llmApiKey: 'sk-...'
   * });
   *
   * console.log(`AI: ${response.response}`);
   * console.log(`Why: ${response.apertureLink}`);
   * ```
   */
  async sendMessage(params: SendMessageParams): Promise<MessageResponse> {
    let conversationId = params.conversationId;

    // Create conversation if not provided
    if (!conversationId) {
      const conv = await this.createConversation(params.userId, params.metadata);
      conversationId = conv.id;
    }

    const data = {
      user_id: params.userId,
      message: params.message,
      llm_provider: params.llmProvider,
      llm_api_key: params.llmApiKey,
      temperature: params.temperature ?? 0.7,
      max_tokens: params.maxTokens ?? 1000,
      ...(params.llmModel && { llm_model: params.llmModel }),
      ...(params.systemPrompt && { system_prompt: params.systemPrompt }),
      ...(params.metadata && { metadata: params.metadata })
    };

    const response = await this.client.post(
      `/v1/conversations/${conversationId}/messages`,
      data
    );

    return {
      conversationId: response.data.conversation_id,
      messageId: response.data.message_id,
      response: response.data.response,
      apertureLink: response.data.aperture_link,
      assessmentCount: response.data.assessment_count,
      provider: response.data.provider,
      model: response.data.model,
      usage: response.data.usage
    };
  }

  /**
   * Create a new conversation
   */
  async createConversation(
    userId: string,
    metadata?: Record<string, any>
  ): Promise<{ id: string; userId: string; metadata: Record<string, any> }> {
    const response = await this.client.post('/v1/conversations', {
      user_id: userId,
      metadata: metadata || {}
    });
    return response.data;
  }

  // ==================== Assessments ====================

  /**
   * Get assessments for a user
   *
   * @param userId - User ID to query
   * @param params - Optional filters
   * @returns List of assessments
   *
   * @example
   * ```typescript
   * // Get all assessments
   * const assessments = await client.getAssessments('user_123');
   *
   * // Get high-confidence technical assessments
   * const tech = await client.getAssessments('user_123', {
   *   element: 'technical_confidence',
   *   minConfidence: 0.8
   * });
   *
   * for (const assessment of tech) {
   *   console.log(`${assessment.element}: ${assessment.value}`);
   *   console.log(`Confidence: ${assessment.confidence}`);
   * }
   * ```
   */
  async getAssessments(
    userId: string,
    params?: GetAssessmentsParams
  ): Promise<Assessment[]> {
    const queryParams: any = {
      limit: params?.limit ?? 50
    };

    if (params?.element) queryParams.element = params.element;
    if (params?.minConfidence !== undefined) queryParams.min_confidence = params.minConfidence;
    if (params?.maxConfidence !== undefined) queryParams.max_confidence = params.maxConfidence;

    const response = await this.client.get(`/v1/users/${userId}/assessments`, {
      params: queryParams
    });

    return response.data.map((a: any) => this.mapAssessment(a));
  }

  /**
   * Get a specific assessment with evidence
   */
  async getAssessment(userId: string, assessmentId: string): Promise<AssessmentWithEvidence> {
    const response = await this.client.get(
      `/v1/users/${userId}/assessments/${assessmentId}`
    );
    return this.mapAssessmentWithEvidence(response.data);
  }

  /**
   * Submit a user correction for an assessment
   *
   * @example
   * ```typescript
   * await client.correctAssessment('user_123', 'assess_456', {
   *   correctionType: 'wrong_value',
   *   userExplanation: "I'm actually very confident with AWS"
   * });
   * ```
   */
  async correctAssessment(
    userId: string,
    assessmentId: string,
    correction: UserCorrection
  ): Promise<Assessment> {
    const response = await this.client.put(
      `/v1/users/${userId}/assessments/${assessmentId}/correct`,
      {
        correction_type: correction.correctionType,
        corrected_value: correction.correctedValue,
        user_explanation: correction.userExplanation
      }
    );
    return this.mapAssessment(response.data);
  }

  // ==================== Pattern Discovery ====================

  /**
   * Discover patterns across all users
   *
   * @param params - Discovery parameters
   * @returns Discovered patterns with suggestions
   *
   * @example
   * ```typescript
   * const result = await client.discoverPatterns({
   *   minUsers: 20,
   *   minOccurrenceRate: 0.25,
   *   lookbackDays: 7
   * });
   *
   * console.log(`Found ${result.patternsFound} patterns`);
   *
   * for (const pattern of result.patterns) {
   *   console.log(`${pattern.name}: ${pattern.detectedIn} users`);
   *   console.log(`Confidence: ${pattern.confidence}`);
   * }
   * ```
   */
  async discoverPatterns(params?: DiscoverPatternsParams): Promise<{
    patternsFound: number;
    patterns: DiscoveredPattern[];
  }> {
    const response = await this.client.post('/v1/admin/discover-patterns', {
      min_users: params?.minUsers ?? 10,
      min_occurrence_rate: params?.minOccurrenceRate ?? 0.2,
      lookback_days: params?.lookbackDays ?? 7
    });
    return response.data;
  }

  // ==================== Constructs ====================

  /**
   * Create a construct from natural language description
   *
   * @param description - What you want to track
   * @returns Suggested templates or generated config
   *
   * @example
   * ```typescript
   * const result = await client.createConstructFromDescription(
   *   "I want to track if users are ready to upgrade"
   * );
   *
   * if (result.matchType === 'template') {
   *   console.log('Found similar templates:');
   *   for (const template of result.suggestedTemplates!) {
   *     console.log(`- ${template.name} (similarity: ${template.similarity})`);
   *   }
   * } else {
   *   console.log('Generated custom construct:');
   *   console.log(result.customGenerated);
   * }
   * ```
   */
  async createConstructFromDescription(
    description: string
  ): Promise<ConstructFromDescriptionResult> {
    const response = await this.client.post('/v1/constructs/from-description', {
      description
    });
    return response.data;
  }

  /**
   * Browse construct templates from the marketplace
   *
   * @example
   * ```typescript
   * // Get all templates
   * const templates = await client.getConstructTemplates();
   *
   * // Search templates
   * const support = await client.getConstructTemplates({
   *   useCase: 'customer support'
   * });
   * ```
   */
  async getConstructTemplates(params?: {
    search?: string;
    useCase?: string;
  }): Promise<ConstructTemplate[]> {
    const response = await this.client.get('/v1/constructs/templates', {
      params
    });
    return response.data.templates || [];
  }

  /**
   * Validate a construct configuration
   */
  async validateConstruct(config: any): Promise<{
    valid: boolean;
    issues?: string[];
    warnings?: string[];
  }> {
    const response = await this.client.post('/v1/constructs/validate', config);
    return response.data;
  }

  // ==================== Helpers ====================

  private mapAssessment(data: any): Assessment {
    return {
      id: data.id,
      userId: data.user_id,
      element: data.element,
      valueType: data.value_type,
      valueData: data.value_data,
      value: this.extractValue(data),
      reasoning: data.reasoning,
      confidence: data.confidence,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
      userCorrected: data.user_corrected,
      observationCount: data.observation_count
    };
  }

  private mapAssessmentWithEvidence(data: any): AssessmentWithEvidence {
    return {
      ...this.mapAssessment(data),
      evidence: data.evidence || []
    };
  }

  private extractValue(data: any): any {
    const { value_type, value_data } = data;
    if (value_type === 'score') return value_data.score;
    if (value_type === 'tag') return value_data.tag;
    if (value_type === 'range') return value_data.range;
    return value_data.text;
  }
}

// ==================== Exports ====================

export default Aperture;
