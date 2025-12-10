"""
database/app_db.py

Small module exposing DB helper functions so tests can import them.
Provides:
- connect_db(uri, dbname)
- seed_db(db)            # insert courses + students
- create_indexes(db)
"""

import os


import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise ValueError(
        "MONGO_URI or MONGO_DB_NAME not set in environment variables or .env file."
    )


COURSES = [
    {
        "course_code": "CSCI-UA.0002",
        "title": "Introduction to Computer Programming (No Prior Experience)",
        "type": "CS Foundation",
        "subject": "CSCI-UA",
        "difficulty": 2,
        "credits": 4,
        "prerequisites": [],
        "description": "An introduction to the fundamentals of computer programming. Students design, write, and debug computer programs. Does not count toward the computer science major.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0003",
        "title": "Introduction to Computer Programming (Limited Prior Experience)",
        "type": "CS Foundation",
        "subject": "CSCI-UA",
        "difficulty": 2,
        "credits": 4,
        "prerequisites": [],
        "description": "Introduces object-oriented programming, recursion, and other important concepts to students who already have had some exposure to programming in the context of building applications using Python. Does not count toward the computer science major.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0004",
        "title": "Introduction to Web Design & Computer Principles",
        "type": "Other/Non-Major",
        "subject": "CSCI-UA",
        "difficulty": 1,
        "credits": 4,
        "prerequisites": [],
        "description": "Introduces the practice of web design and basic principles of computer science, covering web design, graphics and software tools, an overview of hardware/software, and the history and impact of computers and the Internet.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0060",
        "title": "Database Design and Implementation",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003"],
        "description": "Introduces principles and applications of database design and working with data. Students use Python and SQL to study relational and NoSQL databases.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0061",
        "title": "Web Development and Programming",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003", "CSCI-UA.0004"],
        "description": "Provides a practical approach to web technologies and programming, focusing on building interactive, secure, and powerful web programs using client and server side technologies.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0101",
        "title": "Introduction to Computer Science",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003"],
        "description": "How to design algorithms to solve problems and how to translate these algorithms into working computer programs. Intended primarily for computer science majors.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0102",
        "title": "Data Structures",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0101"],
        "description": "Focuses on the use and design of data structures (stacks, queues, linked lists, binary trees), their implementation in a high-level language, and analysis of their effect on algorithm efficiency.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0201",
        "title": "Computer Systems Organization",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102"],
        "description": "Covers the internal structure of computers, machine (assembly) language programming, the use of pointers, logical design of computers, computer architecture, and internal representation of data.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0202",
        "title": "Operating Systems",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 5,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Covers the principles and design of operating systems, including process scheduling and synchronization, deadlocks, memory management (virtual memory), input/output, and file systems.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0310",
        "title": "Basic Algorithms",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102"],
        "description": "Introduction to the study of algorithms, presenting two main themes: designing appropriate data structures and analyzing the efficiency of algorithms that use them. Algorithms studied include sorting, searching, and graph algorithms. [Also requires Discrete Mathematics and a Calculus course.]",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "CSCI-UA.0330",
        "title": "Introduction to Computer Simulation",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": [],
        "description": "Students learn how to do computer simulations of phenomena such as orbits, disease epidemics, musical instruments, and traffic flow, based on mathematical models, numerical methods, and Matlab programming techniques. [Requires Calculus I/Math for Economics II and General Physics.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0520",
        "title": "Undergraduate Research",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "The student is supervised by a faculty member actively engaged in research, potentially leading to publishable results. May be one or two semesters. Honors students write an honors thesis. [Requires permission of the department.]",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0521",
        "title": "Undergraduate Research",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "Continuation of supervised research with a faculty member. A substantial commitment to this work is expected. [Requires permission of the department.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0897",
        "title": "Internship",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "An excellent complement to formal course work, providing practical training and hands-on experience. Credit does not count toward the major. [Restricted to declared majors with specific GPA requirements.]",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0898",
        "title": "Internship",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "An excellent complement to formal course work, providing practical training and hands-on experience. Credit does not count toward the major. [Restricted to declared majors with specific GPA requirements.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0997",
        "title": "Independent Study",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "Students work on an individual basis under the supervision of a full-time faculty member. Does not satisfy the major elective requirement. [Requires permission of the department and specific GPA requirements.]",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0998",
        "title": "Independent Study",
        "type": "Other/Special",
        "subject": "CSCI-UA",
        "difficulty": 0,
        "credits": "1 - 4",
        "prerequisites": [],
        "description": "Students work on an individual basis under the supervision of a full-time faculty member. Does not satisfy the major elective requirement. [Requires permission of the department and specific GPA requirements.]",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0381",
        "title": "Programming Tools for the Data Scientist",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0002", "CSCI-UA.0003"],
        "description": "Building applications in Python using a project-based learning approach. Students use Python packages in a variety of applied areas, such as textual analysis and data visualization. Does not count toward the computer science major.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0421",
        "title": "Numerical Computing",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201", "MATH-UA.0121"],
        "description": "The need for floating-point arithmetic, the IEEE floating-point standard, and the importance of numerical computing in a wide variety of scientific applications. Fundamental types of numerical algorithms: direct methods (e.g., for systems of linear equations), iterative methods (e.g., for a nonlinear equation), and discretization methods (e.g., for a differential equation). Numerical errors: can you trust your answers? Uses graphics and software packages such as Matlab. Programming assignments.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0430",
        "title": "Agile Software Development and DevOps",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Agile software development has come to describe a specific approach and toolset that allow for the requirements of a software project to change as a project progresses without disrupting schedules, budgets, and responsibilities. The field of DevOps, a portmanteau of development and operations has introduced further processes and infrastructure to automate many of the tasks required in such development. Together, Agile's methodology and DevOps' automation have increased the speed, robustness, and scalability with which software is developed today. Upon completion of this course, students will understand the core methodologies, technologies, and tools used in the software industry today.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0453",
        "title": "Theory of Computation",
        "type": "CS Requirement",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0310", "CSCI-UA.0201"],
        "description": "A mathematical approach to studying topics in computer science, such as regular languages and some of their representations (deterministic finite automata, nondeterministic finite automata, regular expressions) and proof of nonregularity. Context-free languages and pushdown automata; proofs that languages are not context-free. Elements of computability theory. Brief introduction to NP-completeness.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0467",
        "title": "Applied Internet Technology",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Applied Internet Technology is a practical introduction to creating modern web applications. It covers full-stack (that is, every aspect of building a database driven web application: server programming, database implementation, frontend markup, styling and interactivity) web development. It includes topics such as database and data model design, web application architecture, separation of logic and presentation, handling user input and processing form data, managing asynchronous processes, strategies for creating real-time web applications, and handling client-side interactivity. Students will use current server and client-side web frameworks and libraries to build dynamic, data-driven sites. Various applications to support development will also be introduced, such as version control, static analysis tools, and build systems.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0469",
        "title": "Natural Language Processing",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Natural Language Processing (aka Computational Linguistics) is an inter-disciplinary field applying methodology of computer science and linguistics to the processing of natural languages (English, Chinese, Spanish, Japanese, etc.). Typical applications include: information extraction (automatically finding information from text); information retrieval (web searches and other applications involving the automatic selection of relevant documents); sentiment analysis (automatic extraction of opinions about a set of issues); and machine translation (automatically translating one natural language to another). Much of the best work in the field combines two methodologies: (1) automatically acquiring statistical information from one set of training documents to use as the basis for probabilistically predicting the distribution of similar information in new documents; (2) using manually encoded linguistic knowledge. For example, many supervised methods of machine learning require: a corpus of text with manually encoded linguistic knowledge, a set of procedures for acquiring statistical patterns from this data and a transducer for predicting these same distinctions in new text. This class will cover linguistic, statistical and computational aspects of this exciting field.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0470",
        "title": "Object-Oriented Programming",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Introduces the important concepts of object-oriented design and languages, including code reuse, data abstraction, inheritance, and dynamic overloading. Covers in depth those features of Java and C++ that support object-oriented programming and gives an overview of other object-oriented languages of interest. Significant programming assignments stressing object-oriented design. Not offered every academic year.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "CSCI-UA.0472",
        "title": "Artificial Intelligence",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201", "CSCI-UA.0310"],
        "description": "Many cognitive tasks that people can do easily and almost unconsciously have proven extremely difficult to program on a computer. Artificial intelligence tackles the problem of developing computer systems that can carry out these tasks. Focus is on three central areas in AI: representation and reasoning, machine learning, and natural language processing.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0473",
        "title": "Fundamentals of Machine Learning",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102", "MATH-UA.0140", "MATH-UA.0185"],
        "description": "This exciting and fast-evolving field of computer science has many recent consumer applications (e.g., Microsoft Kinect, Google Translate, IPhone's Siri, digital camera face detection, Netflix recommendations, Google news) and applications within the sciences and medicine (e.g., predicting protein-protein interactions, species modeling, detecting tumors, personalized medicine). Students learn the theoretical foundations and how to apply machine learning to solve new problems.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0474",
        "title": "Software Engineering",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "An intense hands-on study of practical techniques and methods of software engineering. Topics include advanced object-oriented design, design patterns, refactoring, code optimization, universal modeling language, threading, user interface design, enterprise application development, and development tools. All topics are integrated and applied during the semester long group project. The aim of the project is to prepare students for dynamics in a real workplace. Members of the group meet on a regular basis to discuss the project and to assign individual tasks. Students are judged primarily on the final project presentations. Not offered every academic year.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "CSCI-UA.0475",
        "title": "Predictive Analytics",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201", "CSCI-UA.0310", "MATH-UA.0140"],
        "description": "Predictive analytics is the art and science of extracting useful information from historical data and present data for the purpose of predicting future trends. In this course, students will be introduced to the phases of the analytics life-cycle and will gain an understanding of a variety of tools and machine learning algorithms for analyzing data and discovering forward insights. Several techniques will be introduced including: data preprocessing techniques, data reduction algorithms, data clustering algorithms, data classification algorithms, uplifting algorithms, association rules, data mining algorithms, recommender systems, and more. This course aims to provide students with skills of the new generation of data scientists that will allow them to structure, analyze and derive useful insights from data that could help make better decisions.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0476",
        "title": "Processing Big Data for Analytics Applications",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201", "CSCI-UA.0310"],
        "description": "Introduces platforms, tools, and architectures that facilitate scalable management and processing of vast quantities of data. Explores open source tools enabling the efficient acquisition, distributed storage, and processing of big data. Provides hands-on experience with distributed processing Apache solutions such as Hadoop MapReduce, HBase, Hive, Impala, Pig, core Spark, Spark SQL, and Spark Streaming. Other Apache big data tools covered are Oozie, Zookeeper, Flume, and Kafka.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0478",
        "title": "Introduction to Cryptography",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0310"],
        "description": "An introduction to the principles and practice of cryptography and its application to network security. Topics include symmetric-key encryption (block ciphers, modes of operations, AES), message authentication (pseudorandom functions, CBC-MAC), public-key encryption (RSA, ElGamal), digital signatures (RSA, Fiat-Shamir), and authentication applications (identification, zero-knowledge).",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0479",
        "title": "Data Management and Analysis",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0102"],
        "description": "Extracting, transforming and analyzing data in myriad formats. Using traditional relational databases as well as non-relational databases to store, manipulate, and query data. Students write custom programs, create queries, and use data analysis tools and libraries on a wide array of data sets. Additional topics: data modeling, cloud databases and API programming.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-041",
        "title": "Special Topics: Computer Graphics",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course covering computer graphics. Topics may include rendering, modeling, animation, and graphics programming.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-042",
        "title": "Special Topics: Computer Vision",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course covering computer vision. Topics may include image processing, feature detection, object recognition, and deep learning for vision.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-046",
        "title": "Special Topics: Intro to Social Networking",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course introducing social networking. Topics may include network analysis, social media platforms, graph theory applications, and community detection.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-051",
        "title": "Special Topics: Parallel Computing",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course covering parallel computing. Topics may include parallel algorithms, multi-threading, distributed systems, and performance optimization.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-052",
        "title": "Special Topics: Algorithmic Problem Solving",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 3,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0310"],
        "description": "Special topics course focusing on algorithmic problem solving. Topics may include competitive programming techniques, advanced algorithms, and problem-solving strategies.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-063",
        "title": "Special Topics: Introduction to Computer Security",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course introducing computer security. Topics may include cryptography, network security, system security, and security protocols.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-073",
        "title": "Special Topics: Introduction to Robot Intelligence",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course introducing robot intelligence. Topics may include robotics, autonomous systems, sensor integration, and intelligent control systems.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "CSCI-UA.0480-075",
        "title": "Special Topics: Introduction to Deep Learning",
        "type": "CS Elective",
        "subject": "CSCI-UA",
        "difficulty": 4,
        "credits": 4,
        "prerequisites": ["CSCI-UA.0201"],
        "description": "Special topics course introducing deep learning. Topics may include neural networks, convolutional neural networks, recurrent neural networks, and deep learning frameworks.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0120",
        "title": "Discrete Mathematics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [],
        "description": "This course is a one-semester introduction to discrete mathematics with an emphasis on the understanding, composition and critiquing of mathematical proofs.",
        "semester_offered": ["Spring", "Fall", "Summer"],
    },
    {
        "course_code": "MATH-UA.0121",
        "title": "Calculus I",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": [],
        "description": "Derivatives, antiderivatives, and integrals of functions of one real variable. Trigonometric, inverse trigonometric, logarithmic and exponential functions."
        " Applications, including graphing, maximizing and minimizing functions. Areas and volumes.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0131",
        "title": "Math For Economics I",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": [],
        "description": "This course is only open to Economics Majors and prospective Economics Majors. Elements of calculus and linear algebra are "
        "important to the study of economics.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0122",
        "title": "Calculus II",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Techniques of integration. Further applications. Plane analytic geometry. Polar coordinates and parametric equations. Infinite series, including power series.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0140",
        "title": "Linear Algebra",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": [],
        "description": "Linear algebra is the study of structure-preserving operators on sets (linear operators on vector spaces). Topics include systems of linear equations,"
        " matrix computation and classification, vector spaces, linear transformations and eigenvalues, length and orthogonality, and orthogonal projections for optimization.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0185",
        "title": "Probability and Statistics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "A combination of Theory of Probability and Mathematical Statistics at an elementary level. Probability topics include mathematical treatment of chance,"
        " combinatorics, binomial, Poisson, and Gaussian distributions, law of large numbers, and applications such as coin-tossing or radioactive decay.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0009",
        "title": "Algebra, Trigonometry, and Functions",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 1,
        "credits": "4",
        "prerequisites": [],
        "description": "Intermediate algebra and trigonometry; algebraic, exponential, logarithmic, and trigonometric functions and their graphs. Serves as preparation for "
        "students who do not otherwise place into Discrete Mathematics (MATH-UA 120), Calculus I (MATH-UA 121), Mathematics for Economics I (MATH-UA 131; formerly MATH-UA 211),"
        " Linear Algebra (MATH-UA 140) and some courses in other departments (such as chemistry and economics).",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0123",
        "title": "Calculus III",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0122"],
        "description": "Functions of several variables. Vectors in the plane and space. Partial derivatives with applications. Double and triple integrals. Spherical and"
        " cylindrical coordinates. Surface and line integrals. Divergence, gradient, and curl. Theorem of Gauss and Stokes.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0126",
        "title": "Introduction to Statistics and Data Analysis",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 2,
        "credits": "4",
        "prerequisites": ["MATH-UA.0009"],
        "description": "An introduction to using statistics to understand the world around us. Formulating a hypothesis and collecting data, summarizing and visualizing, "
        "probability distributions, the central limit theorem and the normal distribution, hypothesis testing, confidence intervals, p-values, the power of an experiment, "
        "t-tests and comparing data sets, linear regression, machine learning methods. Assignments will use statistical software packages to analyze data, and throughout the "
        "semester, students will evaluate the implications and responsible practices of collecting and utilizing data.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0129",
        "title": "Honors Calculus III",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0122"],
        "description": "The scope of this honors class will include the usual MATH-UA 123 syllabus; however this class will move faster, covering additional topics and "
        "going deeper. Functions of several variables. Vectors in the plane and space. Partial derivatives with applications, especially Lagrange multipliers. Double and "
        "triple integrals. Spherical and cylindrical coordinates. Surface and line integrals. Divergence, gradient, and curl. Theorem of Gauss and Stokes.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0132",
        "title": "Mathematics for Economics II",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": [],
        "description": "Matrix algebra; eigenvalues; Ordinary differential equations and stability analysis, multivariable integration and (possibly) dynamic optimization.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0133",
        "title": "Mathematics for Economics III",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Further topics in vector calculus. Vector spaces, matrix analysis. Linear and nonlinear programming with applications to game theory.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0144",
        "title": "Introduction to Computer Simulation",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": ["MATH-UA.0121", "PHYS-UA 11"],
        "description": "Simulations of such phenomena as orbits (Kepler problem and N-body problem), epidemic and endemic disease (including evolution in response to the "
        "selective pressure of malaria), musical stringed instruments (piano, guitar, and violin), and traffic flow in a city (with lights, breakdowns, and gridlock). "
        "Simulations are based on mathematical models, numerical methods, and Matlab programming techniques taught in class. Emphasizes use of animation (and sound where "
        "appropriate) to present the results of simulations.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0148",
        "title": "Honors Linear Algebra",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": ["MATH-UA.0009"],
        "description": "This honors section of Linear Algebra is a proof-based course intended for well-prepared students who have already developed some mathematical "
        "maturity and ease with abstraction. Its scope will include the usual Linear Algebra (MATH-UA 140) syllabus; however this class will be faster, more abstract and "
        "proof-based, covering additional topics. Topics covered are: Vector spaces, linear dependence, basis and dimension, matrices, determinants, solving linear "
        "equations, linear transformations, eigenvalues and eigenvectors, diagonalization, inner products, applications.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0228",
        "title": "Fundamental Dynamics of Earth's Atmosphere and Climate",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": ["MATH-UA.0121", "MATH-UA.0123", "MATH-UA.0132"],
        "description": "An introduction to the dynamical processes that drive the circulation of the atmosphere and ocean, and their interaction. This is the core of "
        "climate science. Lectures will be guided by consideration of observations and experiments, but the goal is to develop an understanding of the unifying principles "
        "of planetary fluid dynamics. Topics include the global energy balance, convection and radiation (the greenhouse effect), effects of planetary rotation (the Coriolis "
        "force), structure of the atmospheric circulation (the Hadley cell and wind patterns), structure of the oceanic circulation (wind-driven currents and the thermohaline "
        "circulation), climate and climate variability (including El Nino and anthropogenic warming).",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0230",
        "title": "Introduction to Fluid Dynamics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0123", "MATH-UA.0129", "MATH-UA.0133"],
        "description": "Fluid dynamics is the branch of physics that can describe the flow of blood in the human body, the flight of an insect, or the motions of weather "
        "systems. Key concepts include: the formalism of continuum mechanics; the conservation of mass, energy, and momentum in a fluid; the Euler and Navier-Stokes equations; "
        "and viscosity and vorticity. These concepts are applied to such classic problems in fluid dynamics as potential flow around a cylinder, the propagation of sound and "
        "gravity waves, and the onset of instability in shear flow.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0231",
        "title": "Computability and Incompleteness",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["PHIL-UA.0070", "MATH-UA.0120"],
        "description": "An introduction to the theory of computability and to the major limitative results of mathematical logic, including the undecidability of first-order "
        "logic, Gödel's incompleteness theorems, and Tarski's theorem on the non-definability of truth.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0232",
        "title": "Set Theory",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "An introduction to the basic concepts and results of set theory. Identical to PHIL-UA 73.",
        "semester_offered": ["Occasionally"],
    },
    {
        "course_code": "MATH-UA.0240",
        "title": "Combinatorics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": ["MATH-UA.0122", "MATH-UA.0132"],
        "description": "Techniques for counting and enumeration, including generating functions, the principle of inclusion and exclusion, and Polya counting. Graph "
        "theory. Modern algorithms and data structures for graph theoretic problems.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0248",
        "title": "Theory of Numbers",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": ["MATH-UA.0122", "MATH-UA.0132"],
        "description": "Divisibility and prime numbers. Linear and quadratic congruences. The classical number-theoretic functions. Continued fractions. Diophantine equations.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "MATH-UA.0250",
        "title": "Mathematics of Finance",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0140",
            "MATH-UA.0185",
            "MATH-UA.0333",
            "MATH-UA.0334",
            "MATH-UA.0338",
        ],
        "description": "Introduction to the mathematics of finance. Topics: linear programming with application to pricing. Interest rates and present value. Basic "
        "probability, random walks, central limit theorem, Brownian motion, log-normal model of stock prices. Black-Scholes theory of options. Dynamic programming "
        "with application to portfolio optimization.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "MATH-UA.0251",
        "title": "Intro to Math Modeling",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "Formulation and analysis of mathematical models. Mathematical tools include dimensional analysis, optimization, simulation, probability, and "
        "elementary differential equations. Applications to biology, economics, other areas of science. The necessary mathematical and scientific background is developed "
        "as needed. Students participate in formulating models as well as in analyzing them.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0255",
        "title": "Mathematics and Biology",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 3,
        "credits": "4",
        "prerequisites": ["MATH-UA.0121", "MATH-UA.0132", "BIOL-UA 11"],
        "description": "Intended primarily for premedical students with interest and ability in mathematics. Topics of medical importance using mathematics as a "
        "tool, including control of the heart, optimal principles in the lung, cell membranes, electrophysiology, countercurrent exchange in the kidney, acid-base "
        "balance, muscle, cardiac catheterization, and computer diagnosis. Material from the physical sciences is introduced as needed and developed within the course.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "MATH-UA.0256",
        "title": "Computers in Medicine & Biology",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": ["MATH-UA.0255"],
        "description": "Introduces the student of biology or mathematics to the use of computers as tools for modeling physiological phenomena. The student constructs "
        "two computer models selected from the following list: circulation, gas exchange in the lung, control of cell volume, and the renal countercurrent mechanism. "
        "The student then uses the model to conduct simulated physiological experiments.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0262",
        "title": "Ordinary Diff Equations",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "First- and second-order equations. Series solutions. Laplace transforms. Introduction to partial differential equations and Fourier series.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0263",
        "title": "Partial Diff Equations",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0262"],
        "description": "Many laws of physics are formulated as partial differential equations. This course discusses the simplest examples of such laws as embodied in "
        "the wave equation, the diffusion equation, and Laplace’s equation. Nonlinear conservation laws and the theory of shock waves. Applications to physics, chemistry, "
        "biology, and population dynamics.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0264",
        "title": "Chaos & Dynamical Systems",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Topics include fixed points of one-dimensional maps; linear operators and linear approximations; stability and bifurcation; logistic maps. Cantor "
        "set, fractal sets, symbolic dynamics, conjugacy of maps. Dynamics in two dimensions. Introduction for students with little preparation to the recent discovery "
        "that, in certain regimes, fully deterministic mechanics can produce chaotic behavior.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0268",
        "title": "Honors Ordinary Differential Equations",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0328", "MATH-UA.0325"],
        "description": "This class will develop rigorously the basic theory of Ordinary Differential Equations (ODEs). Existence and uniqueness of solutions to ODEs are "
        "first investigated, for linear and nonlinear problems, set on the real line or the complex plane. More qualitative questions are then considered, about the "
        "behavior of the solutions, with possible prolongations to various topics in Dynamical Systems theory. Applications to Physics and Biology will appear naturally "
        "when discussing examples.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0325",
        "title": "Analysis",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "This course is an introduction to rigorous analysis on the real line. Topics include: the real number system, sequences and series of numbers, "
        "functions of a real variable (continuity and differentiability), the Riemann integral, basic topological notions in a metric space, sequences and series of "
        "functions including Taylor and Fourier series.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0328",
        "title": "Honors Analysis I",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0133",
            "MATH-UA.0129",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "This is an introduction to the rigorous treatment of the foundations of real analysis in one variable. It is based entirely on proofs. Students "
        "are expected to know what a mathematical proof is and are also expected to be able to read a proof before taking this class. Topics include: properties of the "
        "real number system, sequences, continuous functions, topology of the real line, compactness, derivatives, the Riemann integral, sequences of functions, uniform "
        "convergence, infinite series and Fourier series. Additional topics may include: Lebesgue measure and integral on the real line, metric spaces, and analysis on "
        "metric spaces.",
        "semester_offered": ["Occasionally"],
    },
    {
        "course_code": "MATH-UA.0329",
        "title": "Honors Analysis II",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0328"],
        "description": "Continuation of Honors Analysis I (MATH-UA 328). Topics include: metric spaces, differentiation of functions of several real variables, the implicit "
        "and inverse function theorems, Riemann integral on ℝⁿ, Lebesgue measure on ℝⁿ, the Lebesgue integral.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0333",
        "title": "Theory of Probability",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "Introduction to the mathematical techniques of random phenomena occurring in the natural, physical, and social sciences. Axioms of mathematical "
        "probability, combinatorial analysis, binomial distribution, Poisson and normal approximation, random variables and probability distributions, generating functions, "
        "Markov chains, applications.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0334",
        "title": "Mathematical Statistics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": ["MATH-UA.0333"],
        "description": "Introduction to the mathematical foundations and techniques of modern statistical analysis used in the interpretation of data in quantitative "
        "sciences. Mathematical theory of sampling; normal populations and distributions; chi-square, t, and F distributions; hypothesis testing; estimation; confidence "
        "intervals; sequential analysis; correlation, regression, and analysis of variance. Applications to the sciences.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0338",
        "title": "Honors Theory of Probability",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0120",
            "MATH-UA.0123",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "The aim of this class is to introduce students to probability theory, with a greater emphasis on rigor, more material, and a faster pace than "
        "the Theory of Probability class. The material will include discrete and continuous probability, and the most fundamental limit theorems (law of large numbers "
        "and Central Limit Theorem).",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0343",
        "title": "Algebra",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "Introduction to abstract algebraic structures, including groups, rings, and fields. Sets and relations. Congruences and unique factorization of "
        "integers. Groups, permutation groups, homomorphisms and quotient groups. Rings and quotient rings, Euclidean rings, polynomial rings. Fields, finite extensions.",
        "semester_offered": ["Fall", "Spring"],
    },
    {
        "course_code": "MATH-UA.0348",
        "title": "Honors Algebra I",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "Introduction to abstract algebraic structures, including groups, rings, and fields. Sets and relations. Congruences and unique factorization of "
        "integers. Groups, permutation groups, group actions, homomorphisms and quotient groups, direct products, classification of finitely generated abelian groups, "
        "Sylow theorems. Rings, ideals and quotient rings, Euclidean rings, polynomial rings, unique factorization.",
        "semester_offered": ["Occasionally"],
    },
    {
        "course_code": "MATH-UA.0349",
        "title": "Honors Algebra II",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0348", "MATH-UA.0343"],
        "description": "Principal ideal domains, polynomial rings in several variables, unique factorization domains. Fields, finite extensions, constructions with ruler "
        "and compass, Galois theory, solvability by radicals.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0352",
        "title": "Numerical Analysis",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "In numerical analysis one explores how mathematical problems can be analyzed and solved with a computer. As such, numerical analysis has very "
        "broad applications in mathematics, physics, engineering, finance, and the life sciences. This course introduces the subject for mathematics majors. Theory and "
        "practical examples using Matlab will be combined in studying a range of topics ranging from simple root-finding procedures to differential equations and the "
        "finite element method.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0353",
        "title": "Linear and Nonlinear Optimization",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "Optimization is a major part of the toolbox of the applied mathematician, and more broadly of researchers in quantitative sciences including "
        "economics, data science, machine learning, and quantitative social sciences. This course provides an application-oriented introduction to linear programming "
        "and convex optimization, with a balanced combination of theory, algorithms, and numerical implementation.",
        "semester_offered": ["Fall", "Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0375",
        "title": "Topology",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": ["MATH-UA.0325", "MATH-UA.0328"],
        "description": "Metric spaces, topological spaces, compactness, connectedness. Covering spaces and homotopy groups.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0377",
        "title": "Differential Geometry",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "The differential properties of curves and surfaces. Introduction to manifolds and Riemannian geometry.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0382",
        "title": "Functions of a Complex Variable",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [
            "MATH-UA.0123",
            "MATH-UA.0129",
            "MATH-UA.0133",
            "MATH-UA.0140",
            "MATH-UA.0148",
        ],
        "description": "Complex numbers and complex functions. Differentiation and the Cauchy-Riemann equations. Cauchy's theorem and the Cauchy integral formula. "
        "Singularities, residues, Taylor and Laurent series. Fractional linear transformations and conformal mapping. Analytic continuation.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0393",
        "title": "Honors I",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Topics and prerequisites vary.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "MATH-UA.0394",
        "title": "Senior Honors II",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Topics and prerequisites vary by semester.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0395",
        "title": "Special Topics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Lecture-seminar course on advanced topics selected by the instructor. Topics vary yearly. Covers topics not offered regularly: experimental "
        "courses and courses offered on student demand.",
        "semester_offered": ["Occasionally"],
    },
    {
        "course_code": "MATH-UA.0396",
        "title": "Special Topics II",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 4,
        "credits": "4",
        "prerequisites": [],
        "description": "Topics and prerequisites vary.",
        "semester_offered": ["Occasionally"],
    },
    {
        "course_code": "MATH-UA.0397",
        "title": "Honors III",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [],
        "description": "Topics and prerequisites vary.",
        "semester_offered": ["Fall"],
    },
    {
        "course_code": "MATH-UA.0398",
        "title": "Honors IV",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 5,
        "credits": "4",
        "prerequisites": [],
        "description": "Topics and prerequisites vary by semester.",
        "semester_offered": ["Spring"],
    },
    {
        "course_code": "MATH-UA.0897",
        "title": "Internship in Mathematics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 1,
        "credits": "2-4",
        "prerequisites": [],
        "description": "An internship in mathematics is an excellent complement to formal course work. Practical training along with their classroom experience can help "
        "students to explore different career options and gain hands-on experience. An internship is for majors only.",
        "semester_offered": ["Fall", "Summer"],
    },
    {
        "course_code": "MATH-UA.0898",
        "title": "Internship in Mathematics",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 1,
        "credits": "2-4",
        "prerequisites": ["MATH-UA.0897"],
        "description": "Prerequisite: Restricted to declared math majors. Math major or Math joint major with Computer Science or Economics, a 3.0 Cumulative GPA and "
        "3.5 Math Major GPA required. Students have to have completed 50% of their major. The internship will be pass/fail.",
        "semester_offered": ["Spring", "Summer"],
    },
    {
        "course_code": "MATH-UA.0997",
        "title": "Independent Study",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 2,
        "credits": "2-4",
        "prerequisites": [],
        "description": "To register for this course, a student must complete an application form for independent study and have it approved by a faculty sponsor and "
        "the director of undergraduate studies.",
        "semester_offered": ["Fall", "Summer"],
    },
    {
        "course_code": "MATH-UA.0998",
        "title": "Independent Study",
        "type": "Math Course",
        "subject": "MATH-UA",
        "difficulty": 2,
        "credits": "2-4",
        "prerequisites": [],
        "description": "Independent study allows students the chance to engage with a topic not currently offered in the curriculum. It can also be the means towards "
        "an honors research component.",
        "semester_offered": ["Spring", "Summer"],
    },
]


STUDENTS = [
    {
        "name": "Freshman Overzealous",
        "netid": "fresh01",
        "email": "fresh01@example.edu",
        "password": "test123",
        "year": "Freshman",
        "major": "Computer Science",
        "interests": ["AI", "Systems"],
        "completed_courses": [],
        "planned_semesters": [],
    },
    {
        "name": "Sophomore Balanced",
        "netid": "soph01",
        "email": "soph01@example.edu",
        "password": "test123",
        "year": "Sophomore",
        "major": "Computer Science",
        "interests": ["Software Engineering"],
        "completed_courses": ["CSCI-UA.0101", "CSCI-UA.0102"],
        "planned_semesters": [],
    },
]

# Hash passwords for students before inserting into DB
for student in STUDENTS:
    plain_pw = student["password"].encode()
    hashed_pw = bcrypt.hashpw(plain_pw, bcrypt.gensalt())
    student["password"] = hashed_pw.decode()  # store as string


def connect_db(uri=None, db_name=None):
    """Return db handle."""
    uri = uri or MONGO_URI
    db_name = db_name or DB_NAME
    return MongoClient(uri)[db_name]


def create_indexes(db):
    """Create useful indexes (idempotent)."""
    db.courses.create_index("course_code", unique=True)
    db.students.create_index("netid", unique=True)


def seed_db(db, environment="development"):
    """
    Seed the DB with sample courses and students.

    IMPORTANT: Never drops the students collection to preserve user registrations.
    - Courses: Always dropped and re-seeded (they're static reference data that should always be up-to-date)
    - Students: Only seeded if collection is empty (preserves user data)
    """
    students_count = db.students.count_documents({})

    # Handle courses: Always drop and re-seed (courses are static reference data)
    # This ensures courses are always up-to-date when the database is seeded
    db.courses.drop()
    db.courses.insert_many(COURSES)
    courses_added = len(COURSES)

    # Handle students: NEVER drop, only seed test data if collection is empty
    if students_count == 0:
        db.students.insert_many(STUDENTS)
        students_added = len(STUDENTS)
    else:
        students_added = students_count

    create_indexes(db)

    return {
        "courses": courses_added,
        "students": students_added,
    }
