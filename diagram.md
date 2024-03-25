```mermaid 

graph LR
    subgraph Preprocessing
        A[Upload PDF File] --> B[Extract Text]
        B --> C[Split Text into Chunks]
    end
    
    subgraph Language Model Setup
        D[Initialize Language Models]
    end
    
    subgraph Question Generation
        E{Questions Generated?} -->|No| F[Generate Questions]
        E -->|Yes| G[Display Questions]
    end
    
    C --> D
    D --> E
    G --> H[Select Questions to Answer]
    H --> I{Form Submitted?}
    I -->|Yes| J[Create Retrieval QA Chain]
    J --> K[Generate Answers]
    K --> L[Display Questions and Answers]