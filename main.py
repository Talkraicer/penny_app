import streamlit as st
import user
import data_page
import vis_page
import savings_page










def main():
    users = user.load_users()
    if "username" in st.session_state or user.authenticate(users):
        st.session_state.current_user = user.getCurrentUsername()
        st.image("/Users/emilyramim/Desktop/projects /semester 7/נבונות/penny_app/img.png", width=200,
                 caption="Penny App Logo")

        st.title(f"Welcome Back, {st.session_state.current_user}! \U0001F44B")
        st.write(f"here's whats happening with your money today.")
        tab1, tab2, tab3 = st.tabs(["DATA", "VIS", "SAVINGS"])
        if tab1: st.session_state.current_tab = "DATA"
        if tab2: st.session_state.current_tab = "VIS"
        if tab3: st.session_state.current_tab = "SAVINGS"


        with tab1:
            st.write("Data tab")
            data_page.create_upload_drag_drop(user.getCurrentUsername())
            st.session_state.current_tab = "DATA"
        with tab2:
            st.write("Vis tab")
            st.session_state.current_tab = "VIS"
            vis_page.layout()
        with tab3:
            st.write("Savings tab")
            st.session_state.current_tab = "SAVINGS"
            savings_page.layout()

        if st.button("Logout"):
            st.sidebar.success("Logged out")
            st.session_state.pop("username")

    else:
        st.title("Welcome to the Penny App! \U0001F4B0")
        st.write("please register or log in!")
        st.image("/Users/emilyramim/Desktop/projects /semester 7/נבונות/penny_app/img.png", width=800 )





if __name__ == "__main__":
    main()
