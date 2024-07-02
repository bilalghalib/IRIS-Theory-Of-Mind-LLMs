import json

def display_tom(tom):
    print("\nCurrent Theory of Mind:")
    print(json.dumps(tom.to_dict(), indent=2))

def modify_tom(tom):
    print("\nModify Theory of Mind:")
    print("1. Current Frame")
    print("2. Growth Frame")
    frame_choice = input("Choose a frame to modify (1/2): ")
    
    frame = tom.current_frame if frame_choice == "1" else tom.growth_frame
    
    print("\nCategories:")
    print("1. Beliefs")
    print("2. Emotions")
    print("3. Goals")
    print("4. Knowledge")
    print("5. Skills")
    print("6. Challenges")
    
    category_choice = input("Choose a category to modify (1-6): ")
    category_map = {
        "1": "beliefs", "2": "emotions", "3": "goals",
        "4": "knowledge", "5": "skills", "6": "challenges"
    }
    category = category_map.get(category_choice)
    
    if not category:
        print("Invalid category choice.")
        return
    
    elements = getattr(frame, category)
    for i, element in enumerate(elements):
        print(f"{i+1}. {element.content}")
    
    element_choice = input("Choose an element to modify (number) or 'new' to add: ")
    
    if element_choice.lower() == 'new':
        content = input("Enter new content: ")
        confidence = float(input("Enter confidence (0-1): "))
        new_element = Element(content=content, confidence=confidence)
        elements.append(new_element)
        print("New element added.")
    else:
        try:
            index = int(element_choice) - 1
            element = elements[index]
            print(f"Current content: {element.content}")
            print(f"Current confidence: {element.confidence}")
            new_content = input("Enter new content (press enter to keep current): ")
            new_confidence = input("Enter new confidence (0-1, press enter to keep current): ")
            
            if new_content:
                element.content = new_content
            if new_confidence:
                element.confidence = float(new_confidence)
            
            print("Element updated.")
        except (ValueError, IndexError):
            print("Invalid choice.")
