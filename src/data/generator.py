"""Generate synthetic university data: courses, students, and enrollments."""

import json
import random
from pathlib import Path

from src.data.schemas import Course, Enrollment, Student

COURSES: list[dict] = [
    # ── Computer Science (12) ──────────────────────────────────────────
    {
        "id": "CS101", "title": "Introduction to Programming",
        "department": "Computer Science",
        "description": "Learn the fundamentals of programming using Python. Topics include variables, control flow, functions, and basic data structures. Designed for students with no prior coding experience.",
        "tags": ["programming", "python", "beginner", "software"],
        "difficulty": "introductory", "credits": 4, "prerequisites": [],
    },
    {
        "id": "CS150", "title": "Discrete Mathematics for CS",
        "department": "Computer Science",
        "description": "Mathematical foundations for computer science including logic, sets, combinatorics, graph theory, and proof techniques. Essential preparation for algorithms and theory courses.",
        "tags": ["discrete math", "logic", "graphs", "proofs", "combinatorics"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "CS201", "title": "Data Structures and Algorithms",
        "department": "Computer Science",
        "description": "Study of fundamental data structures including arrays, linked lists, trees, hash tables, and graphs. Algorithm design techniques such as divide-and-conquer, dynamic programming, and greedy algorithms.",
        "tags": ["algorithms", "data structures", "complexity", "python"],
        "difficulty": "intermediate", "credits": 4, "prerequisites": ["CS101"],
    },
    {
        "id": "CS210", "title": "Computer Architecture",
        "department": "Computer Science",
        "description": "Organization and design of computer systems. Topics include instruction set architectures, pipelining, memory hierarchies, and parallel processing fundamentals.",
        "tags": ["hardware", "architecture", "assembly", "systems"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["CS101"],
    },
    {
        "id": "CS250", "title": "Computer Security",
        "department": "Computer Science",
        "description": "Principles of computer and network security. Covers threat modeling, cryptographic protocols, authentication systems, web security, and ethical hacking fundamentals.",
        "tags": ["security", "cryptography", "networking", "hacking", "privacy"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["CS201"],
    },
    {
        "id": "CS260", "title": "Database Systems",
        "department": "Computer Science",
        "description": "Design and implementation of relational database systems. SQL, normalization, query optimization, transaction processing, and introduction to NoSQL databases.",
        "tags": ["databases", "SQL", "data modeling", "transactions"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["CS201"],
    },
    {
        "id": "CS270", "title": "Web Development",
        "department": "Computer Science",
        "description": "Full-stack web development using modern frameworks. HTML, CSS, JavaScript, REST APIs, and deployment. Students build a complete web application as a final project.",
        "tags": ["web", "javascript", "HTML", "frontend", "backend", "REST"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["CS101"],
    },
    {
        "id": "CS310", "title": "Operating Systems",
        "department": "Computer Science",
        "description": "Design and implementation of operating systems. Process management, memory management, file systems, concurrency, and synchronization primitives.",
        "tags": ["operating systems", "concurrency", "memory", "processes", "linux"],
        "difficulty": "advanced", "credits": 4, "prerequisites": ["CS201", "CS210"],
    },
    {
        "id": "CS340", "title": "Machine Learning",
        "department": "Computer Science",
        "description": "Introduction to machine learning algorithms including linear regression, decision trees, neural networks, and clustering. Students implement models using scikit-learn and PyTorch.",
        "tags": ["machine learning", "AI", "neural networks", "python", "data science"],
        "difficulty": "advanced", "credits": 4, "prerequisites": ["CS201", "MATH201"],
    },
    {
        "id": "CS350", "title": "Natural Language Processing",
        "department": "Computer Science",
        "description": "Computational methods for understanding and generating human language. Word embeddings, transformers, sentiment analysis, and text generation using modern NLP frameworks.",
        "tags": ["NLP", "language", "transformers", "text mining", "AI"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["CS340"],
    },
    {
        "id": "CS360", "title": "Computer Vision",
        "department": "Computer Science",
        "description": "Image processing and visual recognition using deep learning. Convolutional neural networks, object detection, image segmentation, and generative models for visual data.",
        "tags": ["computer vision", "deep learning", "image processing", "CNN"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["CS340"],
    },
    {
        "id": "CS380", "title": "Applied Cryptography",
        "department": "Computer Science",
        "description": "Mathematical foundations and practical applications of cryptographic systems. Symmetric and asymmetric encryption, digital signatures, zero-knowledge proofs, and blockchain fundamentals.",
        "tags": ["cryptography", "encryption", "blockchain", "security", "math"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["CS250", "MATH201"],
    },
    # ── Mathematics (8) ────────────────────────────────────────────────
    {
        "id": "MATH101", "title": "Calculus I",
        "department": "Mathematics",
        "description": "Limits, derivatives, and integrals of single-variable functions. Applications to physics, economics, and optimization problems.",
        "tags": ["calculus", "derivatives", "integrals", "analysis"],
        "difficulty": "introductory", "credits": 4, "prerequisites": [],
    },
    {
        "id": "MATH102", "title": "Calculus II",
        "department": "Mathematics",
        "description": "Techniques of integration, sequences, series, parametric equations, and polar coordinates. Introduction to multivariable calculus concepts.",
        "tags": ["calculus", "series", "integration", "sequences"],
        "difficulty": "introductory", "credits": 4, "prerequisites": ["MATH101"],
    },
    {
        "id": "MATH201", "title": "Linear Algebra",
        "department": "Mathematics",
        "description": "Vector spaces, linear transformations, matrices, eigenvalues, and applications. Essential for machine learning, physics, and engineering.",
        "tags": ["linear algebra", "matrices", "vectors", "eigenvalues"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["MATH101"],
    },
    {
        "id": "MATH210", "title": "Probability and Statistics",
        "department": "Mathematics",
        "description": "Probability theory, random variables, distributions, hypothesis testing, and regression analysis. Applications to data science and experimental design.",
        "tags": ["probability", "statistics", "distributions", "data analysis"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["MATH102"],
    },
    {
        "id": "MATH250", "title": "Differential Equations",
        "department": "Mathematics",
        "description": "Ordinary differential equations and their applications. First and second order equations, Laplace transforms, systems of equations, and numerical methods.",
        "tags": ["differential equations", "ODE", "modeling", "dynamics"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["MATH102"],
    },
    {
        "id": "MATH301", "title": "Number Theory",
        "department": "Mathematics",
        "description": "Properties of integers, prime numbers, congruences, quadratic reciprocity, and Diophantine equations. Connections to cryptography and coding theory.",
        "tags": ["number theory", "primes", "congruences", "cryptography"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["MATH201"],
    },
    {
        "id": "MATH310", "title": "Abstract Algebra",
        "department": "Mathematics",
        "description": "Groups, rings, and fields with applications to symmetry, coding theory, and cryptography. Explores the algebraic structures underlying modern mathematics.",
        "tags": ["algebra", "groups", "rings", "fields", "symmetry"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["MATH201"],
    },
    {
        "id": "MATH350", "title": "Numerical Analysis",
        "department": "Mathematics",
        "description": "Algorithms for numerical computation: root finding, interpolation, numerical integration, and solving linear systems. Error analysis and stability of numerical methods.",
        "tags": ["numerical methods", "computation", "approximation", "algorithms"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["MATH201", "CS101"],
    },
    # ── Physics (6) ────────────────────────────────────────────────────
    {
        "id": "PHYS101", "title": "General Physics I",
        "department": "Physics",
        "description": "Mechanics, waves, and thermodynamics. Newtonian mechanics, conservation laws, oscillations, and heat transfer with laboratory experiments.",
        "tags": ["mechanics", "waves", "thermodynamics", "lab"],
        "difficulty": "introductory", "credits": 4, "prerequisites": [],
    },
    {
        "id": "PHYS102", "title": "General Physics II",
        "department": "Physics",
        "description": "Electricity, magnetism, optics, and modern physics. Maxwell's equations, electromagnetic waves, interference, and introduction to quantum phenomena.",
        "tags": ["electromagnetism", "optics", "quantum", "electricity"],
        "difficulty": "introductory", "credits": 4, "prerequisites": ["PHYS101"],
    },
    {
        "id": "PHYS201", "title": "Classical Mechanics",
        "department": "Physics",
        "description": "Advanced treatment of Newtonian mechanics using Lagrangian and Hamiltonian formulations. Central forces, rigid body dynamics, and oscillations.",
        "tags": ["mechanics", "Lagrangian", "Hamiltonian", "dynamics"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["PHYS101", "MATH250"],
    },
    {
        "id": "PHYS250", "title": "Quantum Mechanics",
        "department": "Physics",
        "description": "Foundations of quantum theory. Wave functions, Schrodinger equation, angular momentum, hydrogen atom, and perturbation theory.",
        "tags": ["quantum mechanics", "wave functions", "Schrodinger", "atomic physics"],
        "difficulty": "advanced", "credits": 4, "prerequisites": ["PHYS201", "MATH201"],
    },
    {
        "id": "PHYS260", "title": "Computational Physics",
        "department": "Physics",
        "description": "Numerical simulation of physical systems using Python. Monte Carlo methods, molecular dynamics, finite element analysis, and data visualization.",
        "tags": ["simulation", "python", "modeling", "numerical methods", "physics"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["PHYS101", "CS101"],
    },
    {
        "id": "PHYS350", "title": "Quantum Computing",
        "department": "Physics",
        "description": "Principles of quantum computation. Qubits, quantum gates, entanglement, quantum algorithms, and error correction. Hands-on with quantum simulators.",
        "tags": ["quantum computing", "qubits", "algorithms", "entanglement"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["PHYS250", "MATH201"],
    },
    # ── Arts (8) ───────────────────────────────────────────────────────
    {
        "id": "ART101", "title": "Foundations of Visual Art",
        "department": "Arts",
        "description": "Introduction to drawing, painting, and composition. Explores elements of design including line, shape, color theory, and perspective.",
        "tags": ["drawing", "painting", "color theory", "composition", "design"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "ART120", "title": "History of Art",
        "department": "Arts",
        "description": "Survey of visual arts from ancient civilizations to contemporary movements. Examines cultural, social, and political contexts shaping artistic expression.",
        "tags": ["art history", "culture", "movements", "visual arts"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "ART150", "title": "Digital Photography",
        "department": "Arts",
        "description": "Principles of digital photography including exposure, composition, lighting, and post-processing. Students develop a portfolio of original work.",
        "tags": ["photography", "digital", "composition", "lighting", "portfolio"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "ART201", "title": "Graphic Design",
        "department": "Arts",
        "description": "Principles of visual communication and typography. Layout design, branding, and digital media production using industry-standard tools.",
        "tags": ["graphic design", "typography", "branding", "visual communication"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["ART101"],
    },
    {
        "id": "ART220", "title": "Digital Illustration",
        "department": "Arts",
        "description": "Creating illustrations using digital tools and tablets. Character design, concept art, and visual storytelling for games and media.",
        "tags": ["illustration", "digital art", "character design", "concept art"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["ART101"],
    },
    {
        "id": "ART250", "title": "3D Modeling and Animation",
        "department": "Arts",
        "description": "Introduction to 3D modeling, texturing, rigging, and animation using Blender. Students create animated short scenes as final projects.",
        "tags": ["3D modeling", "animation", "Blender", "texturing", "rigging"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["ART101"],
    },
    {
        "id": "ART301", "title": "Interactive Media Art",
        "department": "Arts",
        "description": "Creating interactive art installations using sensors, microcontrollers, and creative coding. Explores the intersection of art, technology, and human interaction.",
        "tags": ["interactive art", "creative coding", "Arduino", "installations"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["ART201"],
    },
    {
        "id": "ART320", "title": "Data Visualization Design",
        "department": "Arts",
        "description": "Designing effective visual representations of data. Principles of information design, chart selection, color mapping, and narrative visualization.",
        "tags": ["data visualization", "information design", "charts", "visual analytics"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["ART201"],
    },
    # ── Literature (8) ────────────────────────────────────────────────
    {
        "id": "LIT101", "title": "Introduction to Literature",
        "department": "Literature",
        "description": "Survey of major literary genres including poetry, fiction, drama, and the essay. Develops close reading and analytical writing skills.",
        "tags": ["literature", "reading", "writing", "analysis", "genres"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "LIT120", "title": "Creative Writing",
        "department": "Literature",
        "description": "Workshop-based course in fiction and poetry writing. Students produce original work and develop their voice through peer critique and revision.",
        "tags": ["creative writing", "fiction", "poetry", "workshop"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "LIT150", "title": "World Literature",
        "department": "Literature",
        "description": "Major works of literature from diverse cultures and traditions. Explores themes of identity, power, and belonging across global literary traditions.",
        "tags": ["world literature", "culture", "identity", "global", "diversity"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "LIT201", "title": "Shakespeare and Renaissance Drama",
        "department": "Literature",
        "description": "In-depth study of Shakespeare's plays and their Renaissance context. Performance, language, and the enduring relevance of early modern drama.",
        "tags": ["Shakespeare", "drama", "Renaissance", "theater", "performance"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["LIT101"],
    },
    {
        "id": "LIT220", "title": "Modern Poetry",
        "department": "Literature",
        "description": "Major movements in 20th and 21st century poetry. Modernism, confessional poetry, spoken word, and experimental forms.",
        "tags": ["poetry", "modernism", "contemporary", "verse", "spoken word"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["LIT101"],
    },
    {
        "id": "LIT250", "title": "Science Fiction and Society",
        "department": "Literature",
        "description": "Critical study of science fiction literature and its engagement with technology, utopia, dystopia, and social change. From Mary Shelley to contemporary authors.",
        "tags": ["science fiction", "dystopia", "technology", "society", "speculative"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["LIT101"],
    },
    {
        "id": "LIT301", "title": "Computational Linguistics",
        "department": "Literature",
        "description": "Introduction to the computational study of language. Corpus analysis, stylometry, digital humanities methods, and how computers process literary texts.",
        "tags": ["computational linguistics", "digital humanities", "corpus", "text analysis"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["LIT101"],
    },
    {
        "id": "LIT320", "title": "Narrative and Game Design",
        "department": "Literature",
        "description": "Storytelling techniques in interactive media. Branching narratives, world-building, dialogue writing, and narrative design for video games.",
        "tags": ["narrative design", "game writing", "storytelling", "interactive fiction"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["LIT120"],
    },
    # ── Business (8) ──────────────────────────────────────────────────
    {
        "id": "BUS101", "title": "Introduction to Business",
        "department": "Business",
        "description": "Overview of business fundamentals including management, marketing, finance, and entrepreneurship. Case studies of successful startups and corporations.",
        "tags": ["business", "management", "marketing", "entrepreneurship"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "BUS120", "title": "Microeconomics",
        "department": "Business",
        "description": "Supply and demand, market structures, consumer behavior, and game theory. Applications to real-world markets and policy decisions.",
        "tags": ["economics", "markets", "supply demand", "game theory"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "BUS150", "title": "Accounting Fundamentals",
        "department": "Business",
        "description": "Principles of financial and managerial accounting. Financial statements, cost analysis, budgeting, and introduction to auditing.",
        "tags": ["accounting", "finance", "budgeting", "financial statements"],
        "difficulty": "introductory", "credits": 3, "prerequisites": [],
    },
    {
        "id": "BUS201", "title": "Marketing Strategy",
        "department": "Business",
        "description": "Consumer behavior, market segmentation, branding, digital marketing, and campaign design. Students develop a marketing plan for a real product.",
        "tags": ["marketing", "branding", "digital marketing", "consumer behavior"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["BUS101"],
    },
    {
        "id": "BUS220", "title": "Financial Management",
        "department": "Business",
        "description": "Corporate finance, investment analysis, risk management, and capital markets. Time value of money, portfolio theory, and valuation methods.",
        "tags": ["finance", "investment", "risk management", "valuation"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["BUS150"],
    },
    {
        "id": "BUS250", "title": "Entrepreneurship and Innovation",
        "department": "Business",
        "description": "From idea to startup: business model canvas, lean methodology, pitching, fundraising, and building a minimum viable product.",
        "tags": ["entrepreneurship", "startups", "innovation", "lean", "MVP"],
        "difficulty": "intermediate", "credits": 3, "prerequisites": ["BUS101"],
    },
    {
        "id": "BUS301", "title": "Business Analytics",
        "department": "Business",
        "description": "Data-driven decision making for business. Statistical analysis, predictive modeling, A/B testing, and dashboard design using real business datasets.",
        "tags": ["analytics", "data science", "business intelligence", "dashboards"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["BUS201", "MATH210"],
    },
    {
        "id": "BUS320", "title": "Technology Product Management",
        "department": "Business",
        "description": "Managing the lifecycle of technology products. User research, roadmapping, agile methodologies, metrics, and cross-functional team leadership.",
        "tags": ["product management", "agile", "user research", "roadmap", "tech"],
        "difficulty": "advanced", "credits": 3, "prerequisites": ["BUS250"],
    },
]

STUDENTS: list[dict] = [
    # Obvious matches
    {"id": "STU001", "name": "Alice Chen", "major": "Computer Science", "year": 3,
     "interests": ["machine learning", "neural networks", "data science"],
     "completed_courses": ["CS101", "CS150", "CS201", "CS210", "MATH101", "MATH201"]},
    {"id": "STU002", "name": "Bob Martinez", "major": "Literature", "year": 2,
     "interests": ["creative writing", "poetry", "fiction"],
     "completed_courses": ["LIT101", "LIT120", "LIT150"]},
    {"id": "STU003", "name": "Priya Sharma", "major": "Mathematics", "year": 4,
     "interests": ["cryptography", "number theory", "abstract algebra"],
     "completed_courses": ["MATH101", "MATH102", "MATH201", "MATH210", "MATH301", "CS101", "CS150"]},
    {"id": "STU004", "name": "James Wilson", "major": "Physics", "year": 3,
     "interests": ["quantum mechanics", "computational physics", "simulation"],
     "completed_courses": ["PHYS101", "PHYS102", "PHYS201", "MATH101", "MATH102", "MATH201", "CS101"]},
    # Cross-domain interests
    {"id": "STU005", "name": "Luna Rivera", "major": "Arts", "year": 2,
     "interests": ["digital art", "programming", "creative coding", "interactive installations"],
     "completed_courses": ["ART101", "ART120", "ART150"]},
    {"id": "STU006", "name": "Omar Hassan", "major": "Computer Science", "year": 2,
     "interests": ["game development", "3D graphics", "storytelling", "character design"],
     "completed_courses": ["CS101", "CS150", "CS201", "MATH101"]},
    {"id": "STU007", "name": "Yuki Tanaka", "major": "Business", "year": 3,
     "interests": ["data analytics", "machine learning", "business intelligence"],
     "completed_courses": ["BUS101", "BUS120", "BUS150", "BUS201", "MATH101", "MATH210"]},
    {"id": "STU008", "name": "Sarah Kim", "major": "Literature", "year": 3,
     "interests": ["computational linguistics", "digital humanities", "text mining", "AI"],
     "completed_courses": ["LIT101", "LIT120", "LIT150", "LIT201", "CS101"]},
    # Niche interests
    {"id": "STU009", "name": "Diego Morales", "major": "Physics", "year": 4,
     "interests": ["quantum computing", "quantum algorithms", "information theory"],
     "completed_courses": ["PHYS101", "PHYS102", "PHYS201", "PHYS250", "MATH101", "MATH102", "MATH201", "CS101", "CS201"]},
    {"id": "STU010", "name": "Emma Johansson", "major": "Arts", "year": 3,
     "interests": ["data visualization", "information design", "visual analytics", "statistics"],
     "completed_courses": ["ART101", "ART120", "ART201", "MATH101"]},
    {"id": "STU011", "name": "Raj Patel", "major": "Computer Science", "year": 4,
     "interests": ["computer security", "ethical hacking", "blockchain", "privacy"],
     "completed_courses": ["CS101", "CS150", "CS201", "CS210", "CS250", "CS260", "MATH101", "MATH201"]},
    {"id": "STU012", "name": "Mei-Lin Wu", "major": "Mathematics", "year": 2,
     "interests": ["numerical methods", "simulation", "scientific computing"],
     "completed_courses": ["MATH101", "MATH102", "MATH201", "CS101"]},
    # Broad interests
    {"id": "STU013", "name": "Carlos Gutierrez", "major": "Business", "year": 1,
     "interests": ["entrepreneurship", "technology", "marketing", "social media"],
     "completed_courses": ["BUS101"]},
    {"id": "STU014", "name": "Aisha Okonkwo", "major": "Computer Science", "year": 1,
     "interests": ["web development", "design", "user experience"],
     "completed_courses": ["CS101"]},
    {"id": "STU015", "name": "Liam O'Brien", "major": "Physics", "year": 2,
     "interests": ["astrophysics", "mathematics", "programming", "data analysis"],
     "completed_courses": ["PHYS101", "PHYS102", "MATH101", "MATH102", "CS101"]},
    {"id": "STU016", "name": "Sofia Petrov", "major": "Literature", "year": 4,
     "interests": ["science fiction", "technology and society", "speculative fiction", "game narratives"],
     "completed_courses": ["LIT101", "LIT120", "LIT150", "LIT201", "LIT220", "LIT250"]},
    # More variety
    {"id": "STU017", "name": "Noah Park", "major": "Business", "year": 2,
     "interests": ["finance", "investment", "economics", "risk analysis"],
     "completed_courses": ["BUS101", "BUS120", "BUS150", "MATH101"]},
    {"id": "STU018", "name": "Fatima Al-Rashid", "major": "Arts", "year": 4,
     "interests": ["photography", "graphic design", "branding", "visual storytelling"],
     "completed_courses": ["ART101", "ART120", "ART150", "ART201", "ART220", "BUS101"]},
    {"id": "STU019", "name": "Alex Nguyen", "major": "Computer Science", "year": 3,
     "interests": ["natural language processing", "linguistics", "chatbots", "text generation"],
     "completed_courses": ["CS101", "CS150", "CS201", "CS260", "CS340", "MATH101", "MATH201"]},
    {"id": "STU020", "name": "Zara Thompson", "major": "Mathematics", "year": 1,
     "interests": ["calculus", "physics", "problem solving"],
     "completed_courses": ["MATH101"]},
]


def generate_enrollments(
    students: list[Student], courses: list[Course]
) -> list[Enrollment]:
    """Generate enrollment records from students' completed_courses."""
    random.seed(42)
    semesters = ["2024-Fall", "2025-Spring", "2025-Fall", "2026-Spring"]
    enrollments: list[Enrollment] = []

    for student in students:
        n_completed = len(student.completed_courses)
        for i, course_id in enumerate(student.completed_courses):
            semester_idx = max(0, len(semesters) - 1 - (n_completed - 1 - i))
            semester = semesters[min(semester_idx, len(semesters) - 1)]
            grade = round(random.uniform(6.0, 10.0), 1)
            enrollments.append(
                Enrollment(
                    student_id=student.id,
                    course_id=course_id,
                    semester=semester,
                    grade=grade,
                )
            )

    return enrollments


def generate_all(output_dir: str = "data/raw") -> None:
    """Generate all synthetic data and write to JSON files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    courses = [Course(**c) for c in COURSES]
    students = [Student(**s) for s in STUDENTS]
    enrollments = generate_enrollments(students, courses)

    (out / "courses.json").write_text(
        json.dumps([c.model_dump() for c in courses], indent=2), encoding="utf-8"
    )
    (out / "students.json").write_text(
        json.dumps([s.model_dump() for s in students], indent=2), encoding="utf-8"
    )
    (out / "enrollments.json").write_text(
        json.dumps([e.model_dump() for e in enrollments], indent=2), encoding="utf-8"
    )

    print(f"Generated {len(courses)} courses, {len(students)} students, "
          f"{len(enrollments)} enrollments in {out}/")


if __name__ == "__main__":
    generate_all()
