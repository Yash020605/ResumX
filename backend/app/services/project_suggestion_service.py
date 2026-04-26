"""
Project suggestion service using RAG model to recommend projects based on resume and job description.
"""
import json
from typing import Dict, Any, List
from app.services.groq_ai_service import GroqAIService


class ProjectSuggestionService:
    """Service for suggesting relevant projects using RAG-based approach."""

    def __init__(self):
        """Initialize the service with Groq AI service."""
        try:
            self.ai_model = GroqAIService()
        except Exception as e:
            print(f"Warning: Failed to initialize Groq AI service: {e}")
            self.ai_model = None
        self.project_knowledge_base = self._load_project_knowledge_base()

    def _load_project_knowledge_base(self) -> List[Dict[str, Any]]:
        """Load project knowledge base with various project templates."""
        return [
            {
                "category": "Web Development",
                "projects": [
                    {
                        "title": "E-commerce Platform",
                        "description": "Full-stack e-commerce application with user authentication, product catalog, shopping cart, and payment integration",
                        "tech_stack": ["React", "Node.js", "Express", "MongoDB", "Stripe API"],
                        "skills_developed": ["Frontend Development", "Backend Development", "Database Design", "Payment Integration", "Authentication"],
                        "difficulty": "intermediate",
                        "estimated_duration": "4-6 weeks",
                        "portfolio_value": "high"
                    },
                    {
                        "title": "Social Media Dashboard",
                        "description": "Analytics dashboard for social media management with real-time data visualization and scheduling features",
                        "tech_stack": ["Vue.js", "Python", "Flask", "PostgreSQL", "Chart.js", "Social Media APIs"],
                        "skills_developed": ["Data Visualization", "API Integration", "Real-time Updates", "Dashboard Design"],
                        "difficulty": "intermediate",
                        "estimated_duration": "3-4 weeks",
                        "portfolio_value": "high"
                    },
                    {
                        "title": "Task Management System",
                        "description": "Collaborative project management tool with team features, task tracking, and progress visualization",
                        "tech_stack": ["Angular", "Spring Boot", "MySQL", "WebSocket", "JWT"],
                        "skills_developed": ["Team Collaboration Features", "Real-time Communication", "Project Management", "Security"],
                        "difficulty": "intermediate",
                        "estimated_duration": "3-5 weeks",
                        "portfolio_value": "high"
                    }
                ]
            },
            {
                "category": "Data Science & Analytics",
                "projects": [
                    {
                        "title": "Customer Churn Prediction Model",
                        "description": "Machine learning model to predict customer churn with data preprocessing, feature engineering, and model deployment",
                        "tech_stack": ["Python", "Pandas", "Scikit-learn", "Flask", "Docker", "AWS"],
                        "skills_developed": ["Machine Learning", "Data Preprocessing", "Feature Engineering", "Model Deployment", "Cloud Services"],
                        "difficulty": "intermediate",
                        "estimated_duration": "3-4 weeks",
                        "portfolio_value": "high"
                    },
                    {
                        "title": "Sales Analytics Dashboard",
                        "description": "Interactive dashboard for sales data analysis with predictive insights and automated reporting",
                        "tech_stack": ["Python", "Streamlit", "Plotly", "SQL", "Pandas", "Prophet"],
                        "skills_developed": ["Data Analysis", "Business Intelligence", "Predictive Analytics", "Data Visualization"],
                        "difficulty": "beginner",
                        "estimated_duration": "2-3 weeks",
                        "portfolio_value": "medium"
                    },
                    {
                        "title": "Recommendation System",
                        "description": "Content-based and collaborative filtering recommendation engine for e-commerce or streaming platforms",
                        "tech_stack": ["Python", "TensorFlow", "Pandas", "FastAPI", "Redis", "Docker"],
                        "skills_developed": ["Recommendation Algorithms", "Deep Learning", "API Development", "Caching", "System Design"],
                        "difficulty": "advanced",
                        "estimated_duration": "4-6 weeks",
                        "portfolio_value": "high"
                    }
                ]
            },
            {
                "category": "Mobile Development",
                "projects": [
                    {
                        "title": "Expense Tracker App",
                        "description": "Mobile app for personal finance management with budget tracking, expense categorization, and financial insights",
                        "tech_stack": ["React Native", "Firebase", "Chart.js", "AsyncStorage"],
                        "skills_developed": ["Mobile Development", "State Management", "Local Storage", "Data Visualization", "User Experience"],
                        "difficulty": "beginner",
                        "estimated_duration": "2-3 weeks",
                        "portfolio_value": "medium"
                    },
                    {
                        "title": "Fitness Tracking App",
                        "description": "Health and fitness app with workout tracking, progress monitoring, and social features",
                        "tech_stack": ["Flutter", "Dart", "SQLite", "REST APIs", "Push Notifications"],
                        "skills_developed": ["Cross-platform Development", "Local Database", "Health APIs", "Notifications", "UI/UX Design"],
                        "difficulty": "intermediate",
                        "estimated_duration": "4-5 weeks",
                        "portfolio_value": "high"
                    }
                ]
            },
            {
                "category": "DevOps & Cloud",
                "projects": [
                    {
                        "title": "CI/CD Pipeline Setup",
                        "description": "Complete DevOps pipeline with automated testing, deployment, and monitoring for a web application",
                        "tech_stack": ["Jenkins", "Docker", "Kubernetes", "AWS/Azure", "Terraform", "Prometheus"],
                        "skills_developed": ["Continuous Integration", "Container Orchestration", "Infrastructure as Code", "Monitoring", "Cloud Deployment"],
                        "difficulty": "advanced",
                        "estimated_duration": "3-4 weeks",
                        "portfolio_value": "high"
                    },
                    {
                        "title": "Microservices Architecture",
                        "description": "Design and implement microservices-based application with service discovery, load balancing, and fault tolerance",
                        "tech_stack": ["Spring Boot", "Docker", "Kubernetes", "API Gateway", "Service Mesh", "MongoDB"],
                        "skills_developed": ["Microservices Design", "Service Communication", "Scalability", "Fault Tolerance", "Distributed Systems"],
                        "difficulty": "advanced",
                        "estimated_duration": "5-6 weeks",
                        "portfolio_value": "high"
                    }
                ]
            },
            {
                "category": "AI & Machine Learning",
                "projects": [
                    {
                        "title": "Chatbot with NLP",
                        "description": "Intelligent chatbot using natural language processing for customer service or personal assistance",
                        "tech_stack": ["Python", "NLTK", "spaCy", "TensorFlow", "Flask", "WebSocket"],
                        "skills_developed": ["Natural Language Processing", "Deep Learning", "Conversational AI", "Real-time Communication"],
                        "difficulty": "intermediate",
                        "estimated_duration": "3-4 weeks",
                        "portfolio_value": "high"
                    },
                    {
                        "title": "Computer Vision App",
                        "description": "Image recognition and processing application for object detection, classification, or OCR",
                        "tech_stack": ["Python", "OpenCV", "TensorFlow", "Keras", "Flask", "PIL"],
                        "skills_developed": ["Computer Vision", "Image Processing", "Deep Learning", "Model Training", "API Development"],
                        "difficulty": "intermediate",
                        "estimated_duration": "3-5 weeks",
                        "portfolio_value": "high"
                    }
                ]
            },
            {
                "category": "Blockchain & Web3",
                "projects": [
                    {
                        "title": "DeFi Lending Platform",
                        "description": "Decentralized lending platform with smart contracts, yield farming, and liquidity pools",
                        "tech_stack": ["Solidity", "Web3.js", "React", "Hardhat", "MetaMask", "IPFS"],
                        "skills_developed": ["Smart Contract Development", "DeFi Protocols", "Web3 Integration", "Blockchain Security"],
                        "difficulty": "advanced",
                        "estimated_duration": "6-8 weeks",
                        "portfolio_value": "high"
                    },
                    {
                        "title": "NFT Marketplace",
                        "description": "Complete NFT marketplace with minting, trading, and auction features",
                        "tech_stack": ["Solidity", "Next.js", "Ethers.js", "IPFS", "OpenSea API", "Polygon"],
                        "skills_developed": ["NFT Standards", "Smart Contracts", "Decentralized Storage", "Crypto Payments"],
                        "difficulty": "advanced",
                        "estimated_duration": "5-7 weeks",
                        "portfolio_value": "high"
                    }
                ]
            }
        ]

    def suggest_projects(
        self,
        resume: str,
        job_description: str = "",
        matching_skills: List[str] = None,
        missing_skills: List[str] = None,
        career_fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest relevant projects based on resume, job description, and skill analysis.

        Args:
            resume: Resume text
            job_description: Job description text (optional)
            matching_skills: List of matching skills from analysis
            missing_skills: List of missing skills from analysis
            career_fields: List of relevant career fields

        Returns:
            Dictionary with project suggestions
        """
        try:
            # Create context for project suggestion
            context = self._build_context(resume, job_description, matching_skills, missing_skills, career_fields)
            
            # Get relevant projects from knowledge base
            relevant_projects = self._retrieve_relevant_projects(context)
            
            # Use AI to rank and customize project suggestions
            suggestions = self._generate_project_suggestions(context, relevant_projects)
            
            return {
                "success": True,
                "projects": suggestions,
                "total": len(suggestions),
                "context": {
                    "focus_areas": context.get("focus_areas", []),
                    "skill_gaps": missing_skills or [],
                    "career_alignment": career_fields or []
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Project suggestion failed: {str(e)}",
                "projects": [],
                "total": 0
            }

    def _build_context(
        self,
        resume: str,
        job_description: str,
        matching_skills: List[str],
        missing_skills: List[str],
        career_fields: List[str]
    ) -> Dict[str, Any]:
        """Build context for project suggestions."""
        context = {
            "resume_summary": resume[:1000],  # First 1000 chars
            "job_requirements": job_description[:500] if job_description else "",
            "matching_skills": matching_skills or [],
            "missing_skills": missing_skills or [],
            "career_fields": career_fields or [],
            "focus_areas": []
        }
        
        # Determine focus areas based on missing skills and career fields
        if missing_skills:
            context["focus_areas"].extend([f"Develop {skill}" for skill in missing_skills[:3]])
        
        if career_fields:
            context["focus_areas"].extend([f"Build portfolio for {field}" for field in career_fields[:2]])
        
        return context

    def _retrieve_relevant_projects(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant projects from knowledge base based on context."""
        relevant_projects = []
        
        # Get all projects from knowledge base
        all_projects = []
        for category in self.project_knowledge_base:
            for project in category["projects"]:
                project_with_category = project.copy()
                project_with_category["category"] = category["category"]
                all_projects.append(project_with_category)
        
        # Simple relevance scoring based on skill overlap
        for project in all_projects:
            relevance_score = self._calculate_project_relevance(project, context)
            if relevance_score > 0.3:  # Threshold for relevance
                project["relevance_score"] = relevance_score
                relevant_projects.append(project)
        
        # Sort by relevance score
        relevant_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_projects[:8]  # Return top 8 projects

    def _calculate_project_relevance(self, project: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate relevance score between project and context."""
        score = 0.0
        
        # Check skill overlap
        project_skills = set([skill.lower() for skill in project.get("skills_developed", [])])
        project_tech = set([tech.lower() for tech in project.get("tech_stack", [])])
        
        # Boost score for missing skills (skills to develop)
        missing_skills = set([skill.lower() for skill in context.get("missing_skills", [])])
        skill_overlap = project_skills.intersection(missing_skills)
        score += len(skill_overlap) * 0.3
        
        # Boost score for matching skills (existing expertise)
        matching_skills = set([skill.lower() for skill in context.get("matching_skills", [])])
        tech_overlap = project_tech.intersection(matching_skills)
        score += len(tech_overlap) * 0.2
        
        # Career field alignment
        career_fields = [field.lower() for field in context.get("career_fields", [])]
        project_category = project.get("category", "").lower()
        for field in career_fields:
            if field in project_category or project_category in field:
                score += 0.4
                break
        
        # Base score for all projects
        score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0

    def _generate_project_suggestions(
        self,
        context: Dict[str, Any],
        relevant_projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use AI to generate customized project suggestions with explanations."""
        
        # If AI model is not available, use fallback immediately
        if self.ai_model is None:
            print("AI model not available, using fallback suggestions")
            return self._generate_fallback_suggestions(relevant_projects[:6], context)
        
        # Prepare projects data for AI
        projects_data = []
        for project in relevant_projects:
            projects_data.append({
                "title": project["title"],
                "description": project["description"],
                "tech_stack": project["tech_stack"],
                "skills_developed": project["skills_developed"],
                "difficulty": project["difficulty"],
                "category": project["category"],
                "relevance_score": project["relevance_score"]
            })
        
        prompt = f"""
Based on the user's profile and available projects, provide personalized project recommendations with explanations.

User Context:
- Missing Skills: {', '.join(context.get('missing_skills', []))}
- Matching Skills: {', '.join(context.get('matching_skills', []))}
- Career Fields: {', '.join(context.get('career_fields', []))}
- Focus Areas: {', '.join(context.get('focus_areas', []))}

Available Projects:
{json.dumps(projects_data, indent=2)}

For each project, provide a customized recommendation with:
1. Why it's recommended for this user
2. How it addresses their skill gaps
3. Career benefits
4. Learning outcomes

Respond with ONLY valid JSON in this format:
{{
    "recommendations": [
        {{
            "project_id": "unique_id",
            "title": "Project Title",
            "description": "Project description",
            "tech_stack": ["tech1", "tech2"],
            "skills_developed": ["skill1", "skill2"],
            "difficulty": "beginner/intermediate/advanced",
            "estimated_duration": "X weeks",
            "category": "Category Name",
            "relevance_score": 0.85,
            "why_recommended": "Personalized explanation why this project suits the user",
            "skill_gap_addressed": ["specific skills this project will help develop"],
            "career_benefits": "How this project helps career progression",
            "learning_outcomes": ["specific things user will learn"],
            "portfolio_value": "high/medium/low",
            "next_steps": ["step1", "step2", "step3"]
        }}
    ]
}}
"""
        
        try:
            response = self.ai_model._call_groq(prompt, max_tokens=2000)
            result = self.ai_model._parse_json_response(response)
            
            recommendations = result.get("recommendations", [])
            
            # Add unique IDs and ensure all fields are present
            for i, rec in enumerate(recommendations):
                rec["project_id"] = f"proj_{i+1}"
                
                # Ensure all required fields with defaults
                defaults = {
                    "why_recommended": "This project aligns with your career goals and skill development needs.",
                    "skill_gap_addressed": context.get("missing_skills", [])[:3],
                    "career_benefits": "Enhances your portfolio and demonstrates practical skills to employers.",
                    "learning_outcomes": rec.get("skills_developed", [])[:3],
                    "portfolio_value": "high",
                    "next_steps": [
                        "Set up development environment",
                        "Create project structure and basic components",
                        "Implement core features and functionality",
                        "Add testing and documentation",
                        "Deploy and showcase the project"
                    ]
                }
                
                for key, default_value in defaults.items():
                    if key not in rec:
                        rec[key] = default_value
            
            return recommendations[:6]  # Return top 6 recommendations
            
        except Exception as e:
            print(f"AI suggestion generation failed: {e}")
            # Fallback to basic recommendations
            return self._generate_fallback_suggestions(relevant_projects[:6], context)

    def _generate_fallback_suggestions(
        self,
        projects: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate fallback suggestions when AI fails."""
        suggestions = []
        
        for i, project in enumerate(projects):
            suggestion = {
                "project_id": f"proj_{i+1}",
                "title": project["title"],
                "description": project["description"],
                "tech_stack": project["tech_stack"],
                "skills_developed": project["skills_developed"],
                "difficulty": project["difficulty"],
                "estimated_duration": project["estimated_duration"],
                "category": project["category"],
                "relevance_score": project["relevance_score"],
                "why_recommended": f"This {project['difficulty']} level project helps you develop {', '.join(project['skills_developed'][:2])} skills.",
                "skill_gap_addressed": list(set(project["skills_developed"]).intersection(set(context.get("missing_skills", [])))),
                "career_benefits": f"Builds expertise in {project['category']} and enhances your portfolio.",
                "learning_outcomes": project["skills_developed"][:3],
                "portfolio_value": project["portfolio_value"],
                "next_steps": [
                    "Research project requirements and technologies",
                    "Set up development environment",
                    "Create project plan and milestones",
                    "Start with basic implementation",
                    "Iterate and improve based on feedback"
                ]
            }
            suggestions.append(suggestion)
        
        return suggestions