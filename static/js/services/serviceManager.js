/**
 * Service Manager - Coordinates all application services
 * Manages service lifecycle, dependencies, and communication
 */

class ServiceManager {
    constructor(eventBus, config, domUtils, performance) {
        this.eventBus = eventBus;
        this.config = config;
        this.domUtils = domUtils;
        this.performance = performance;
        
        // Services registry
        this.services = new Map();
        this.serviceStatus = new Map();
        this.serviceDependencies = new Map();
        
        // Initialization state
        this.isInitialized = false;
        this.initializationPromise = null;
        
        this.init();
    }
    
    init() {
        console.log('ServiceManager initializing...');
        this.eventBus.emit('services:manager:initializing');
        
        // Set up service dependency graph
        this.setupDependencies();
        
        console.log('ServiceManager initialized');
        this.eventBus.emit('services:manager:ready');
    }
    
    /**
     * Set up service dependencies
     */
    setupDependencies() {
        // API service has no dependencies
        this.serviceDependencies.set('api', []);
        
        // Settings service depends on API
        this.serviceDependencies.set('settings', ['api']);
        
        // Screenshot service depends on API
        this.serviceDependencies.set('screenshot', ['api']);
        
        // ROI service depends on API
        this.serviceDependencies.set('roi', ['api']);
        
        // Monitoring service depends on API
        this.serviceDependencies.set('monitoring', ['api']);
    }
    
    /**
     * Initialize all services in dependency order
     * @returns {Promise<boolean>}
     */
    async initializeServices() {
        if (this.isInitialized) {
            console.log('Services already initialized');
            return true;
        }
        
        if (this.initializationPromise) {
            console.log('Services initialization in progress');
            return this.initializationPromise;
        }
        
        this.initializationPromise = this._performInitialization();
        return this.initializationPromise;
    }
    
    /**
     * Perform the actual service initialization
     * @returns {Promise<boolean>}
     * @private
     */
    async _performInitialization() {
        const initTimer = this.performance.start('services:initialization');
        
        try {
            console.log('Starting service initialization...');
            this.eventBus.emit('services:initialization:start');
            
            // Load service modules dynamically
            const serviceModules = await this.loadServiceModules();
            
            // Initialize services in dependency order
            const initOrder = this.getInitializationOrder();
            
            for (const serviceName of initOrder) {
                await this.initializeService(serviceName, serviceModules[serviceName]);
            }
            
            this.isInitialized = true;
            
            console.log('All services initialized successfully');
            this.eventBus.emit('services:initialization:complete', {
                services: Array.from(this.services.keys()),
                duration: this.performance.end(initTimer)
            });
            
            return true;
            
        } catch (error) {
            console.error('Service initialization failed:', error);
            this.eventBus.emit('services:initialization:error', { error: error.message });
            throw error;
        }
    }
    
    /**
     * Load all service modules
     * @returns {Promise<Object>}
     */
    async loadServiceModules() {
        const loadTimer = this.performance.start('services:loading');
        
        try {
            console.log('Loading service modules...');
            
            const [
                ApiService,
                ScreenshotService,
                RoiService,
                MonitoringService,
                SettingsService
            ] = await Promise.all([
                import('./api.js').then(m => m.default),
                import('./screenshot.js').then(m => m.default),
                import('./roi.js').then(m => m.default),
                import('./monitoring.js').then(m => m.default),
                import('./settings.js').then(m => m.default)
            ]);
            
            const duration = this.performance.end(loadTimer);
            console.log(`Service modules loaded in ${duration.toFixed(2)}ms`);
            
            return {
                api: ApiService,
                screenshot: ScreenshotService,
                roi: RoiService,
                monitoring: MonitoringService,
                settings: SettingsService
            };
            
        } catch (error) {
            this.performance.end(loadTimer);
            console.error('Failed to load service modules:', error);
            throw error;
        }
    }
    
    /**
     * Get service initialization order based on dependencies
     * @returns {Array<string>}
     */
    getInitializationOrder() {
        const order = [];
        const visited = new Set();
        const visiting = new Set();
        
        const visit = (serviceName) => {
            if (visited.has(serviceName)) return;
            if (visiting.has(serviceName)) {
                throw new Error(`Circular dependency detected involving ${serviceName}`);
            }
            
            visiting.add(serviceName);
            
            const dependencies = this.serviceDependencies.get(serviceName) || [];
            for (const dep of dependencies) {
                visit(dep);
            }
            
            visiting.delete(serviceName);
            visited.add(serviceName);
            order.push(serviceName);
        };
        
        for (const serviceName of this.serviceDependencies.keys()) {
            visit(serviceName);
        }
        
        return order;
    }
    
    /**
     * Initialize a specific service
     * @param {string} serviceName 
     * @param {Class} ServiceClass 
     * @returns {Promise<Object>}
     */
    async initializeService(serviceName, ServiceClass) {
        if (this.services.has(serviceName)) {
            console.log(`Service ${serviceName} already initialized`);
            return this.services.get(serviceName);
        }
        
        const serviceTimer = this.performance.start(`service:${serviceName}:init`);
        
        try {
            console.log(`Initializing ${serviceName} service...`);
            this.serviceStatus.set(serviceName, 'initializing');
            this.eventBus.emit('services:service:initializing', { serviceName });
            
            // Check dependencies
            const dependencies = this.serviceDependencies.get(serviceName) || [];
            for (const dep of dependencies) {
                if (!this.services.has(dep)) {
                    throw new Error(`Dependency ${dep} not available for ${serviceName}`);
                }
            }
            
            // Create service instance with dependencies
            const serviceInstance = this.createServiceInstance(serviceName, ServiceClass, dependencies);
            
            // Register service
            this.services.set(serviceName, serviceInstance);
            this.serviceStatus.set(serviceName, 'ready');
            
            const duration = this.performance.end(serviceTimer);
            console.log(`${serviceName} service initialized in ${duration.toFixed(2)}ms`);
            
            this.eventBus.emit('services:service:ready', { 
                serviceName, 
                service: serviceInstance,
                duration
            });
            
            return serviceInstance;
            
        } catch (error) {
            this.performance.end(serviceTimer);
            this.serviceStatus.set(serviceName, 'error');
            console.error(`Failed to initialize ${serviceName} service:`, error);
            
            this.eventBus.emit('services:service:error', { 
                serviceName, 
                error: error.message 
            });
            
            throw error;
        }
    }
    
    /**
     * Create service instance with proper dependencies
     * @param {string} serviceName 
     * @param {Class} ServiceClass 
     * @param {Array<string>} dependencies 
     * @returns {Object}
     */
    createServiceInstance(serviceName, ServiceClass, dependencies) {
        switch (serviceName) {
            case 'api':
                return new ServiceClass(this.eventBus, this.config);
                
            case 'settings':
                return new ServiceClass(
                    this.services.get('api'),
                    this.eventBus,
                    this.config
                );
                
            case 'screenshot':
                return new ServiceClass(
                    this.services.get('api'),
                    this.eventBus,
                    this.config
                );
                
            case 'roi':
                return new ServiceClass(
                    this.services.get('api'),
                    this.eventBus,
                    this.config
                );
                
            case 'monitoring':
                return new ServiceClass(
                    this.services.get('api'),
                    this.eventBus,
                    this.config
                );
                
            default:
                throw new Error(`Unknown service: ${serviceName}`);
        }
    }
    
    /**
     * Get a service by name
     * @param {string} serviceName 
     * @returns {Object|null}
     */
    getService(serviceName) {
        return this.services.get(serviceName) || null;
    }
    
    /**
     * Check if a service is available
     * @param {string} serviceName 
     * @returns {boolean}
     */
    hasService(serviceName) {
        return this.services.has(serviceName) && this.serviceStatus.get(serviceName) === 'ready';
    }
    
    /**
     * Get service status
     * @param {string} serviceName 
     * @returns {string}
     */
    getServiceStatus(serviceName) {
        return this.serviceStatus.get(serviceName) || 'not-initialized';
    }
    
    /**
     * Get all available services
     * @returns {Object}
     */
    getAllServices() {
        const result = {};
        for (const [name, service] of this.services) {
            if (this.serviceStatus.get(name) === 'ready') {
                result[name] = service;
            }
        }
        return result;
    }
    
    /**
     * Restart a specific service
     * @param {string} serviceName 
     * @returns {Promise<Object>}
     */
    async restartService(serviceName) {
        console.log(`Restarting ${serviceName} service...`);
        this.eventBus.emit('services:service:restarting', { serviceName });
        
        try {
            // Destroy existing service
            await this.destroyService(serviceName);
            
            // Reload and reinitialize
            const serviceModules = await this.loadServiceModules();
            const service = await this.initializeService(serviceName, serviceModules[serviceName]);
            
            console.log(`${serviceName} service restarted successfully`);
            this.eventBus.emit('services:service:restarted', { serviceName, service });
            
            return service;
            
        } catch (error) {
            console.error(`Failed to restart ${serviceName} service:`, error);
            this.eventBus.emit('services:service:restart:error', { serviceName, error: error.message });
            throw error;
        }
    }
    
    /**
     * Destroy a specific service
     * @param {string} serviceName 
     * @returns {Promise<void>}
     */
    async destroyService(serviceName) {
        const service = this.services.get(serviceName);
        if (!service) {
            console.log(`Service ${serviceName} not found`);
            return;
        }
        
        try {
            console.log(`Destroying ${serviceName} service...`);
            this.serviceStatus.set(serviceName, 'destroying');
            
            // Call destroy method if available
            if (typeof service.destroy === 'function') {
                await service.destroy();
            }
            
            this.services.delete(serviceName);
            this.serviceStatus.delete(serviceName);
            
            console.log(`${serviceName} service destroyed`);
            this.eventBus.emit('services:service:destroyed', { serviceName });
            
        } catch (error) {
            console.error(`Error destroying ${serviceName} service:`, error);
            this.serviceStatus.set(serviceName, 'error');
            throw error;
        }
    }
    
    /**
     * Get service health status
     * @returns {Object}
     */
    getHealthStatus() {
        const status = {
            healthy: true,
            services: {},
            errors: [],
            summary: {
                total: this.services.size,
                ready: 0,
                error: 0,
                initializing: 0
            }
        };
        
        for (const [name, service] of this.services) {
            const serviceStatus = this.serviceStatus.get(name);
            const serviceHealth = {
                status: serviceStatus,
                available: serviceStatus === 'ready',
                stats: null
            };
            
            // Get service stats if available
            if (serviceStatus === 'ready' && typeof service.getStats === 'function') {
                try {
                    serviceHealth.stats = service.getStats();
                } catch (error) {
                    serviceHealth.error = error.message;
                    status.errors.push(`${name}: ${error.message}`);
                }
            }
            
            status.services[name] = serviceHealth;
            
            // Update summary
            switch (serviceStatus) {
                case 'ready':
                    status.summary.ready++;
                    break;
                case 'error':
                    status.summary.error++;
                    status.healthy = false;
                    break;
                case 'initializing':
                    status.summary.initializing++;
                    break;
            }
        }
        
        return status;
    }
    
    /**
     * Export service configuration
     * @returns {Object}
     */
    exportConfig() {
        const config = {
            services: {},
            dependencies: Object.fromEntries(this.serviceDependencies),
            status: Object.fromEntries(this.serviceStatus)
        };
        
        // Get config from each service
        for (const [name, service] of this.services) {
            if (typeof service.getStats === 'function') {
                try {
                    config.services[name] = service.getStats();
                } catch (error) {
                    config.services[name] = { error: error.message };
                }
            }
        }
        
        return config;
    }
    
    /**
     * Get service manager statistics
     * @returns {Object}
     */
    getStats() {
        return {
            initialized: this.isInitialized,
            serviceCount: this.services.size,
            readyServices: Array.from(this.serviceStatus.entries())
                .filter(([, status]) => status === 'ready')
                .map(([name]) => name),
            errorServices: Array.from(this.serviceStatus.entries())
                .filter(([, status]) => status === 'error')
                .map(([name]) => name),
            dependencies: Object.fromEntries(this.serviceDependencies)
        };
    }
    
    /**
     * Cleanup all services
     * @returns {Promise<void>}
     */
    async destroy() {
        console.log('Destroying ServiceManager...');
        this.eventBus.emit('services:manager:destroying');
        
        // Destroy services in reverse dependency order
        const destroyOrder = this.getInitializationOrder().reverse();
        
        for (const serviceName of destroyOrder) {
            try {
                await this.destroyService(serviceName);
            } catch (error) {
                console.error(`Error destroying ${serviceName}:`, error);
            }
        }
        
        this.services.clear();
        this.serviceStatus.clear();
        this.isInitialized = false;
        this.initializationPromise = null;
        
        console.log('ServiceManager destroyed');
        this.eventBus.emit('services:manager:destroyed');
    }
}

export default ServiceManager;
